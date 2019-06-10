
# coding: utf-8

# In[1]:


# imports
import sys
import time
import json
from functools import partial
from twisted.web import server, resource
from twisted.internet import reactor, protocol, task
from twisted.internet.serialport import SerialPort

MAGIC_NUMBER = 170

TIME_INFINITY = 2000000000


# In[2]:


# class InmoovSerial
def b16(x):
    return (x //256) & 0xFF, x & 0xFF

def bstr(s):
    return [len(s)] + [ord(c) for c in s]

CANCELING = False
def cancel_task(task):
    global CANCELING
    CANCELING = True
    task.cancel()
    CANCELING = False

def later(*args, **kwargs):
    if CANCELING:
        return
    print(*args, **kwargs)
    import traceback
    traceback.print_stack()

def deferLater(*a, **kwa):
    d = task.deferLater(*a, **kwa)
    #d.addCallback(print)
    d.addErrback(later)
    return d

class MrlcommProtocol(protocol.Protocol):
    device_id_next = 1
    _last_message_sent = 0
    _next_message_slot = 0
    _inter_message_delay = 0.005
    def __init__(self, name, callback = None):
        self._buffer = []
        self.name = name
        self.callback = callback if callback else print
        self.devices = {}
        self._next_message_slot

    def connectionMade(self):
        print(self.name, self.transport)

    def connectionLost(self, reason):
        print(self.name, 'connection lost called')

    def dataReceived(self, data):
        self._buffer.extend(data)
        while len(self._buffer)>= 3: # magic, len, type
            magic, msg_len, msg_type = self._buffer[:3]
            if magic != MAGIC_NUMBER:
                print('BAD MAGIC', magic, 'flushing', self._buffer)
                self._buffer = []
                return
            if len(self._buffer) < 2 + msg_len:
                return
            self.callback(self, msg_type, self._buffer[3:msg_len+2] )
            self._buffer = self._buffer[msg_len+2:]
    
    def message_send(self, data):
        now = time.time()
        if now < self._last_message_sent + self._inter_message_delay:
            #print('defering', data,  self._next_message_slot - now, self._last_message_sent + self._inter_message_delay - now)
            deferLater(reactor, (self._next_message_slot - now)*1.3, self.message_send, data=data)
            self._next_message_slot += self._inter_message_delay
            return
        self._last_message_sent = now
        self._next_message_slot = max(self._next_message_slot, now + self._inter_message_delay)

        msg = [MAGIC_NUMBER, len(data)] + data
        self.transport.writeSomeData(bytes(msg))

 # mrlcommands
    def c_get_board_info(self):
        self.message_send([GET_BOARD_INFO])
        
    def c_servo_attach(self, device_id, pin, init_pos, init_velocity, name):
        self.message_send([SERVO_ATTACH, device_id, pin, *b16(init_pos), *b16(init_velocity), *bstr(name)])
    
    def c_servo_attach_pin(self, device_id, pin):
        self.message_send([SERVO_ATTACH_PIN, device_id, pin])
    
    def c_servo_detach_pin(self, device_id):
        self.message_send([SERVO_DETACH_PIN, device_id])
    
    def c_servo_move_to_microseconds(self, device_id, target):
        self.message_send([SERVO_MOVE_TO_MICROSECONDS, device_id, *b16(target)])

    def c_servo_set_velocity(self, device_id, velocity):
        self.message_send([SERVO_SET_VELOCITY, device_id, *b16(velocity)])

 # device abstraction
    def servo_add(self, device, pin, init_pos, init_velocity, name):
        device_id = self.device_id_next
        self.device_id_next += 1
        self.c_servo_attach(device_id, pin, init_pos, init_velocity, name)
        self.devices[device_id] = device
        return device_id


# In[3]:


#commands

# < publishMRLCommError/str errorMsg
PUBLISH_MRLCOMM_ERROR = 1
# > getBoardInfo
GET_BOARD_INFO = 2
# < publishBoardInfo/version/boardType/b16 microsPerLoop/b16 sram/activePins/[] deviceSummary
PUBLISH_BOARD_INFO = 3
# > enablePin/address/type/b16 rate
ENABLE_PIN = 4
# > setDebug/bool enabled
SET_DEBUG = 5
# > setSerialRate/b32 rate
SET_SERIAL_RATE = 6
# > softReset
SOFT_RESET = 7
# > enableAck/bool enabled
ENABLE_ACK = 8
# < publishAck/function
PUBLISH_ACK = 9
# > echo/f32 myFloat/myByte/f32 secondFloat
ECHO = 10
# < publishEcho/f32 myFloat/myByte/f32 secondFloat
PUBLISH_ECHO = 11
# > customMsg/[] msg
CUSTOM_MSG = 12
# < publishCustomMsg/[] msg
PUBLISH_CUSTOM_MSG = 13
# > deviceDetach/deviceId
DEVICE_DETACH = 14
# > i2cBusAttach/deviceId/i2cBus
I2C_BUS_ATTACH = 15
# > i2cRead/deviceId/deviceAddress/size
I2C_READ = 16
# > i2cWrite/deviceId/deviceAddress/[] data
I2C_WRITE = 17
# > i2cWriteRead/deviceId/deviceAddress/readSize/writeValue
I2C_WRITE_READ = 18
# < publishI2cData/deviceId/[] data
PUBLISH_I2C_DATA = 19
# > neoPixelAttach/deviceId/pin/b32 numPixels
NEO_PIXEL_ATTACH = 20
# > neoPixelSetAnimation/deviceId/animation/red/green/blue/b16 speed
NEO_PIXEL_SET_ANIMATION = 21
# > neoPixelWriteMatrix/deviceId/[] buffer
NEO_PIXEL_WRITE_MATRIX = 22
# > analogWrite/pin/value
ANALOG_WRITE = 23
# > digitalWrite/pin/value
DIGITAL_WRITE = 24
# > disablePin/pin
DISABLE_PIN = 25
# > disablePins
DISABLE_PINS = 26
# > pinMode/pin/mode
PIN_MODE = 27
# < publishDebug/str debugMsg
PUBLISH_DEBUG = 28
# < publishPinArray/[] data
PUBLISH_PIN_ARRAY = 29
# > setTrigger/pin/triggerValue
SET_TRIGGER = 30
# > setDebounce/pin/delay
SET_DEBOUNCE = 31
# > servoAttach/deviceId/pin/b16 initPos/b16 initVelocity/str name
SERVO_ATTACH = 32
# > servoAttachPin/deviceId/pin
SERVO_ATTACH_PIN = 33
# > servoDetachPin/deviceId
SERVO_DETACH_PIN = 34
# > servoSetVelocity/deviceId/b16 velocity
SERVO_SET_VELOCITY = 35
# > servoSweepStart/deviceId/min/max/step
SERVO_SWEEP_START = 36
# > servoSweepStop/deviceId
SERVO_SWEEP_STOP = 37
# > servoMoveToMicroseconds/deviceId/b16 target
SERVO_MOVE_TO_MICROSECONDS = 38
# > servoSetAcceleration/deviceId/b16 acceleration
SERVO_SET_ACCELERATION = 39
# < publishServoEvent/deviceId/eventType/b16 currentPos/b16 targetPos
PUBLISH_SERVO_EVENT = 40
# > serialAttach/deviceId/relayPin
SERIAL_ATTACH = 41
# > serialRelay/deviceId/[] data
SERIAL_RELAY = 42
# < publishSerialData/deviceId/[] data
PUBLISH_SERIAL_DATA = 43
# > ultrasonicSensorAttach/deviceId/triggerPin/echoPin
ULTRASONIC_SENSOR_ATTACH = 44
# > ultrasonicSensorStartRanging/deviceId
ULTRASONIC_SENSOR_START_RANGING = 45
# > ultrasonicSensorStopRanging/deviceId
ULTRASONIC_SENSOR_STOP_RANGING = 46
# < publishUltrasonicSensorData/deviceId/b16 echoTime
PUBLISH_ULTRASONIC_SENSOR_DATA = 47
# > setAref/b16 type
SET_AREF = 48
# > motorAttach/deviceId/type/[] pins
MOTOR_ATTACH = 49
# > motorMove/deviceId/pwr
MOTOR_MOVE = 50
# > motorMoveTo/deviceId/pos
MOTOR_MOVE_TO = 51


# In[4]:


def get_serial(name, path):
    protocol = MrlcommProtocol(name)
    SerialPort(protocol, path, reactor=reactor, baudrate=115200),
    return protocol

serials_dict = {
    'left' : get_serial('left', '/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_55635303838351319072-if00'),
    'right': get_serial('right', '/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_7563331313335161B131-if00'),
}


# In[5]:


servos_list_keys = [
    'name', 'serial_name', 'pin', 'degree_init', 'degree_min', 'degree_max', 'is_inverted',
]
servos_list_raw_left = [
    ('left_thumb', 'left', 2, 145, 0, 180, False),
    ('left_index', 'left', 3, 145, 0, 180, False),
    ('left_middle', 'left', 4, 145, 0, 180, False),
    ('left_ring', 'left', 5, 145, 0, 180, False),
    ('left_little', 'left', 6, 145, 0, 180, False),
    ('left_wrist', 'left', 7, 90, 0, 180, False),

    ('left_bicep', 'left', 8, 45, 0, 90, False),
    ('left_rotate', 'left', 9, 90, 40, 180, False),
    ('left_shoulder', 'left', 10, 90, 0, 180, False),
    ('left_omoplate', 'left', 11, 10, 10, 80, False),

    ('head_eyex', 'left', 22, 90, 70, 110, False),
    ('head_eyey', 'left', 24, 90, 60, 120, False),
    ('head_jaw', 'left', 26, 90, 60, 120, False), # TODO connect
    ('head_neck', 'left', 12, 20, 0, 100, False),
    ('head_rothead', 'left', 13, 90, 0, 180, False),
    ('head_rollneck', 'left', 30, 90, 0, 180, False), # huh 
    ('torso_top', 'left', 27, 90, 70, 110, False),
    ('torso_mid', 'left', 28, 90, 0, 180, False),    
]
servos_list_raw_right = [
    ('right_thumb', 'right', 2, 140, 0, 140, True),
    ('right_index', 'right', 3, 140, 0, 140, True),
    ('right_middle', 'right', 7, 140, 0, 140, True),#set to wrist, was 4
    ('right_ring', 'right', 5, 140, 0, 140, True),
    ('right_little', 'right', 6, 140, 0, 140, True),
    #('right_wrist', 'right', 7, 100, 0, 180, True), # disabled

    ('right_bicep', 'right', 8, 45, 0, 90, False),
    ('right_rotate', 'right', 9, 90, 40, 180, False),
    ('right_shoulder', 'right', 10, 90, 0, 180, False),
    ('right_omoplate', 'right', 11, 10, 10, 80, False),
]

servos_list = [{k:v for k,v in zip(servos_list_keys, servo)} for servo in servos_list_raw_right+servos_list_raw_left]


# In[6]:


# class Servo
SERVO_EVENT_STOPPED = 1
SERVO_EVENT_POSITION_UPDATE = 2

def angle_to_microseconds(degree):
    # from https://github.com/MyRobotLab/myrobotlab/blob/05ef7ca86b67623593e2e94089202b63f676aa02/src/org/myrobotlab/service/Arduino.java#L147
    return (degree * (2400 - 544) // 180) + 544

class Servo():
    is_attached = False
    detach_task = None

    def __init__(self, serial_name, pin, degree_init, name, degree_min=0, degree_max=180, velocity_init=0xFFFF, is_inverted=False):
        self.serial = serials_dict[serial_name]
        self.pin = pin
        self.pos_init = angle_to_microseconds(degree_init)
        self.pos_min = angle_to_microseconds(degree_min)
        self.pos_max = angle_to_microseconds(degree_max)
        self.velocity = velocity_init
        self.name = name
        
        self.is_inverted = is_inverted
        if self.is_inverted:
            self.clip = self.clip_inverted
        else:
            self.clip = self.clip_normal

        self.pos_curr = self.clip(self.pos_init)

        self.device_id = self.serial.servo_add(self, self.pin, self.pos_curr, self.velocity, self.name)
        self.is_attached = True

    def __str__(self):
        return self.name
    
    def clip_normal(self, pos):
        return max(min(pos, self.pos_max), self.pos_min)

    def clip_inverted(self, pos):
        return self.pos_max + self.pos_min - max(min(pos, self.pos_max), self.pos_min)

    def move_to(self, degree, velocity=None):
        # TODO compute how much time this move should take
        if not self.is_attached:
            self.attach()
        if self.detach_task:
            print('canceling detach', self.name, self.detach_task)
            cancel_task(self.detach_task)
            self.detach_task = None
        if velocity is not None and self.velocity != velocity:
            self.set_velocity(velocity)
        pos_new = angle_to_microseconds(degree)
        self.pos_curr = self.clip(pos_new)
        print(pos_new, self.pos_curr, self.pos_min, self.pos_max)
        self.serial.c_servo_move_to_microseconds(self.device_id, self.pos_curr)

    def set_velocity(self, velocity):
        if not self.is_attached:
            self.attach()
        self.velocity = velocity
        self.serial.c_servo_set_velocity(self.device_id, velocity)

    def attach(self):
        self.serial.c_servo_attach_pin(self.device_id, self.pin)
        self.is_attached = True

    def detach(self):
        try:
            print('detaching', self)
        except Exception as e:
            print('!!!!!!!', e)
            raise
        if self.is_attached:
            self.serial.c_servo_detach_pin(self.device_id)
            self.is_attached = False
            self.detach_task = None
        print('detached', self)


# In[7]:


class Robot():
    detach_delay = 1.5
    def __init__(self, serials_dict, servos_list, reactor):
        self.serials_dict = serials_dict
        self.servos_list = servos_list
        self.reactor = reactor
        self.servos_dict = {}
        self.moving_servos = {} #name => last_change
        
        for s in self.serials_dict.values():
            s.callback = self.message_callback
        for s_d in self.servos_list:
            self.servos_dict[s_d['name']] = None

    def message_callback(self, serial, msg_type, msg):
        if msg_type == PUBLISH_ACK:
            #print('ack', [int(__) for __ in msg])
            pass
        elif msg_type == PUBLISH_SERVO_EVENT:
            device_id = msg[0]
            event_type = msg[1]
            pos_current = msg[2]*256 + msg[3]
            pos_target = msg[4]*256 + msg[5]
            servo = serial.devices[device_id]
            #print('servo', servo, 'publish event', device_id, event_type, pos_current, pos_target)
            if event_type == SERVO_EVENT_STOPPED: #and servo.name in self.moving_servos:
                print('servo', servo, 'stop')
                if servo.detach_task:
                    cancel_task(servo.detach_task)
                servo.detach_task = deferLater(self.reactor, self.detach_delay, servo.detach)
                #del self.moving_servos[servo.name]
        elif msg_type == PUBLISH_BOARD_INFO:
            print('publish board info')
        elif msg_type == SOFT_RESET:
            print('serial', serial, 'did a soft reset !?!?!?!?!?')
        else:
            print('robot got message from', serial, 'type', msg_type, [b for b in msg])

    def servos_start(self, delay=0.0, velocity_init=10):
        print('trying to start servos')
        for s_d in self.servos_list:
            if s_d['name'] in self.servos_dict and self.servos_dict[s_d['name']] is not None:
                print('skippin already existing servo', s_d['name'])
                continue
            print('init of', s_d['name'])
            s = Servo(velocity_init=velocity_init, **s_d)
            self.servos_dict[s_d['name']] = s
            time.sleep(delay)
        print('done trying to start servos')

    def killall(self):
        print('killall')
        for s in self.servos_dict.values():
            s.detach()
        print('done killall')
    
    def move_to(self, servo_name, degree, velocity=None):
        print('move_to', servo_name, degree, velocity)
        if servo_name not in self.servos_dict:
            raise Exception('servo {} is not in servos_dict'.format(servo_name))
        servo = self.servos_dict[servo_name]
        servo.move_to(degree, velocity)
        self.moving_servos[servo_name] = 0 # TODO time?
    


# In[8]:


class RobotResource(resource.Resource):
    isLeaf = True
    def __init__(self, *args, robot=None, **kwargs):
        assert robot is not None
        self.robot = robot
        return super().__init__(*args, **kwargs)
    def render_GET(self, request):
        return "Use POST".encode('utf-8')
    def render_POST(self, request):
        newdata = request.content.getvalue()
        commands = json.loads(newdata.decode())
        errors = []
        for c in commands:
            print(c)
            command_type = c['type']
            #defer = partial(task.deferLater, reactor, c['time_after'])
            def defer(fn, *args, **kwargs):
                def fn_w():
                    try:
                        return fn(*args,**kwargs)
                    except Exception as e:
                        import traceback
                        print('EEEEEE', e)
                        traceback.print_exc()
                        raise
                return task.deferLater(reactor, c['time_after'], fn_w)
            if command_type == 'servos_start':
                d = defer(self.robot.servos_start)
                d.addErrback(later)
            elif command_type == 'move_to':
                if c['servo_name'] in self.robot.servos_dict and self.robot.servos_dict[c['servo_name']] is not None:
                    d = defer(self.robot.move_to, c['servo_name'], c['degree'], c.get('velocity'))
                else:
                    errors.append('bad servo name: {}'.format(c['servo_name']))
            elif command_type == 'set_detach_delay':
                self.robot.detach_delay = c['detach_delay']
            elif command_type == 'print':
                d = defer(print, *c['args'])
            elif command_type == 'killall':
                defer(self.robot.killall)
            elif command_type == 'killall_hard':
                self.robot.killall()
        
        if errors:
            return ('\n'.join(['!']+errors)).encode('utf-8')
        return "yay".encode('utf-8')


# In[9]:


site = server.Site(RobotResource(
    robot = Robot(serials_dict, servos_list, reactor)
))
reactor.listenTCP(8081, site)
reactor.run()

