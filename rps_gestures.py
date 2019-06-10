
# coding: utf-8

# In[ ]:


import requests
import time
import subprocess
url = None


def send(data):
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(response.text)
        raise


# In[ ]:


fingers = ['_thumb', '_index', '_middle', '_ring', '_little']
def rock(hand, after=0, velocity=None):
    for i, f in enumerate(fingers):
        yield {'time_after':after, 'type':'move_to', 'servo_name':hand+f, 'degree':1, 'velocity':velocity}
        
def paper(hand, after=0, velocity=None):
    for i, f in enumerate(fingers):
        yield {'time_after':after, 'type':'move_to', 'servo_name':hand+f, 'degree':180, 'velocity':velocity}
        
def scissors(hand, after=0, velocity=None):
    return [
        {'time_after':after, 'type':'move_to', 'servo_name':hand+fingers[0], 'degree':65, 'velocity':velocity},
        {'time_after':after, 'type':'move_to', 'servo_name':hand+fingers[1], 'degree':180, 'velocity':velocity},
        {'time_after':after, 'type':'move_to', 'servo_name':hand+fingers[2], 'degree':180, 'velocity':velocity},
        {'time_after':after, 'type':'move_to', 'servo_name':hand+fingers[3], 'degree':5, 'velocity':velocity},
        {'time_after':after, 'type':'move_to', 'servo_name':hand+fingers[4], 'degree':5, 'velocity':velocity},
        {'time_after':after+1, 'type':'move_to', 'servo_name':hand+fingers[0], 'degree':5, 'velocity':velocity},
    ]

def play(sign, selected_hand, s=1.5):
    # sign: rock, paper, scissors
    # rock
    do_rock = list(rock(selected_hand, after=0.05, velocity=90))
    send(do_rock)

    # wrist
    send([
        {'time_after':0.1, 'type':'move_to', 'servo_name': selected_hand + '_wrist', 'degree': 0, 'velocity': 40}
    ])

    
    up_1 = 0.15
    down_1 = up_1 + 1.4
    up_2 = down_1 + 0.7
    down_2 = up_2 + 1.2
    up_3 = down_2 + 0.7
    down_3 = up_3 + 1.2
    sign_time = down_3 + 0.2
    
    shoulder_up_velocity = 40
    shoulder_down_velocity = 50
    bicep_up_velocity = 40
    bicep_down_velocity = 60
    
    delay = 0.05
    
    def upscale(a):
        a['time_after'] *= s
        return a
    send([upscale(a) for a in [
        ## go up
        {'time_after':up_1, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':150, 'velocity':shoulder_up_velocity},
        {'time_after':up_1 + delay , 'type':'move_to', 'servo_name': selected_hand + '_bicep', 
         'degree':70, 'velocity': bicep_up_velocity},

        # go down
        {'time_after':down_1, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':110, 'velocity':shoulder_down_velocity},
        {'time_after':down_1 + delay, 'type':'move_to', 'servo_name': selected_hand + '_bicep', 
         'degree':10, 'velocity': bicep_down_velocity},

        ## go up
        {'time_after':up_2, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':150, 'velocity':shoulder_up_velocity},
        {'time_after':up_2 + delay, 'type':'move_to', 'servo_name': selected_hand +'_bicep', 
         'degree':70, 'velocity': bicep_up_velocity},

        # go down
        {'time_after':down_2, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':110, 'velocity':shoulder_down_velocity},
        {'time_after':down_2 + delay, 'type':'move_to', 'servo_name': selected_hand + '_bicep', 
         'degree':10, 'velocity': bicep_down_velocity},

        ## go up
        {'time_after':up_3, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':150, 'velocity':shoulder_up_velocity},
        {'time_after':up_3 + delay, 'type':'move_to', 'servo_name': selected_hand + '_bicep', 
         'degree':70, 'velocity': bicep_up_velocity},

        # go down
        {'time_after':down_3, 'type':'move_to', 'servo_name': selected_hand + '_shoulder', 
         'degree':110, 'velocity':shoulder_down_velocity},
        {'time_after':down_3 + delay, 'type':'move_to', 'servo_name': selected_hand +'_bicep', 
         'degree':10, 'velocity': bicep_down_velocity},

    ]])
    
    
    if sign == 'rock':
        selected_action = rock
    elif sign == 'paper':
        selected_action = paper
    elif sign == 'scissors':
        selected_action = scissors

    do_action = list(selected_action(selected_hand, after=sign_time * s, velocity=160))
    send(do_action)
    
    return (sign_time+1)*s # time to do all the moves



# In[ ]:


def setup(url_ = 'http://9.138.226.113:8081', killall_delay=8):
    global url
    if url is not None:
        raise Exception('url is already setup')
    url = url_
    send([
        {'time_after':0, 'type':'servos_start'},
        {'time_after':killall_delay, 'type':'killall'},
    ])
    time.sleep(killall_delay+1)


# In[ ]:


def init():
    #open_hand = list(paper('left', after=0, velocity=90)) + list(paper('right', after=0, velocity=90))
    open_hand = list(paper('right', after=0, velocity=90))
    send(open_hand)

    send([
        {'time_after':0, 'type':'move_to', 'servo_name':'right_shoulder', 'degree':90},
        #{'time_after':0.1, 'type':'move_to', 'servo_name':'left_shoulder', 'degree':90},
        {'time_after':0.2, 'type':'move_to', 'servo_name':'right_bicep', 'degree':0},
        #{'time_after':0.3, 'type':'move_to', 'servo_name':'left_bicep', 'degree':0},
    ])
    return 2


# In[ ]:


def play_soundfile(file):
    subprocess.call(['play', file])
    #subprocess.call(['sudo', '-u', speak_user, 'play', 'one.wav'], env={'DISPLAY':speak_display})

def sound_sequence_with_play(s=1.5, speak_user='taufer', speak_display=':0'):
    time.sleep(s*2.0)
    play_soundfile('one.wav')
    time.sleep(s*1.7)
    play_soundfile('two.wav')
    time.sleep(s*1.3)
    play_soundfile('three.wav')
    


# In[ ]:


if __name__ == '__main__':
    setup()
    send([{'type': 'set_detach_delay', 'detach_delay': 5.0}])
    init()
    time.sleep(3.5)
    
    s = 1.5
    
    all_time = play(sign='paper', selected_hand='left', s=s)


# In[ ]:


if __name__ == '__main__':
    selected_hand='right'
    init()


# In[33]:


if __name__ == '__main__':
    #a = random.choice(actions)
    #print(a)
    url = 'http://9.138.226.113:8081'
    play('rock', 'left')
    #play('rock', 'right')

