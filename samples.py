
# coding: utf-8

# In[ ]:


import rps_gestures


# In[ ]:


rps_gestures.send(
    [
        {'time_after':0, 'type':'move_to', 'servo_name':'head_rothead', 'degree':35, 'velocity':50},
        {'time_after':0, 'type':'move_to', 'servo_name':'head_eyex', 'degree':180, 'velocity':25},
        {'time_after':2.0, 'type':'move_to', 'servo_name':'head_rothead', 'degree':145, 'velocity':50},
        {'time_after':2.0, 'type':'move_to', 'servo_name':'head_eyex', 'degree':0, 'velocity':25},
        {'time_after':5.4, 'type':'move_to', 'servo_name':'head_rothead', 'degree':90, 'velocity':50},
        {'time_after':5.4, 'type':'move_to', 'servo_name':'head_eyex', 'degree':90, 'velocity':25},
        
    ]
)
rps_gestures.send(
    [
        {'time_after':0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':0, 'velocity':190},
        {'time_after':1.0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':180, 'velocity':190},
        {'time_after':2.0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':0, 'velocity':190},
        {'time_after':3.0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':180, 'velocity':190},
        {'time_after':4.0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':0, 'velocity':190},
        {'time_after':5.0, 'type':'move_to', 'servo_name':'head_jaw', 'degree':0, 'velocity':190},
        
        
    ]
)


# In[ ]:


rps_gestures.send(
    [
        {'time_after':0, 'type':'move_to', 'servo_name':'right_omoplate', 'degree':45, 'velocity':35},
        {'time_after':0, 'type':'move_to', 'servo_name':'right_shoulder', 'degree':155, 'velocity':35},
        {'time_after':0, 'type':'move_to', 'servo_name':'right_bicep', 'degree':80, 'velocity':35},
        {'time_after':2, 'type':'move_to', 'servo_name':'right_omoplate', 'degree':0, 'velocity':35},
        {'time_after':2, 'type':'move_to', 'servo_name':'right_shoulder', 'degree':90, 'velocity':35},
        {'time_after':2, 'type':'move_to', 'servo_name':'right_bicep', 'degree':25, 'velocity':35},
        {'time_after':4, 'type':'move_to', 'servo_name':'right_shoulder', 'degree':55, 'velocity':35},
        {'time_after':4, 'type':'move_to', 'servo_name':'right_bicep', 'degree':80, 'velocity':35},
        {'time_after':4, 'type':'move_to', 'servo_name':'right_rotate', 'degree':155, 'velocity':35},
        
        {'time_after':6, 'type':'move_to', 'servo_name':'right_omoplate', 'degree':0, 'velocity':35},
        {'time_after':6, 'type':'move_to', 'servo_name':'right_shoulder', 'degree':90, 'velocity':35},
        {'time_after':6, 'type':'move_to', 'servo_name':'right_bicep', 'degree':25, 'velocity':35},
        {'time_after':6, 'type':'move_to', 'servo_name':'right_rotate', 'degree':90, 'velocity':35},
        
    ]
)



# In[ ]:


rps_gestures.send(
    [
        {'time_after':0, 'type':'move_to', 'servo_name':'torso_mid', 'degree':135, 'velocity':35},
        {'time_after':0.2, 'type':'move_to', 'servo_name':'head_rothead', 'degree':130, 'velocity':15},
        {'time_after':2.2, 'type':'move_to', 'servo_name':'torso_mid', 'degree':90, 'velocity':35},
        {'time_after':2.4, 'type':'move_to', 'servo_name':'head_rothead', 'degree':90, 'velocity':15},

    ]
)


# In[ ]:


rps_gestures.send(
    [
        {'time_after':0, 'type':'move_to', 'servo_name':'torso_top', 'degree':135, 'velocity':35},
        
        {'time_after':1.5, 'type':'move_to', 'servo_name':'torso_top', 'degree':45, 'velocity':35},
        
        {'time_after':3.7, 'type':'move_to', 'servo_name':'torso_top', 'degree':95, 'velocity':35},
        
    ]
)


# In[ ]:


rps_gestures.send([     
    {'time_after':0, 'type':'move_to', 'servo_name':'right_omoplate', 'degree':75, 'velocity':35},
    {'time_after':3., 'type':'move_to', 'servo_name':'right_omoplate', 'degree':0, 'velocity':35},
                  ])

