'''
Created on 2017-07-18

@author: tareq80
'''




#!/usr/bin/python


import socket
import sys
import rospy
import numpy


from sensor_msgs.msg import JointState
from sensor_msgs.msg import Joy


class main(object):
    
    def __init__(self):
        
              
        #rospy.init_node('joint_state_publisher')
        #topic = '/oculus'  
        
        # change topic please
        self.pub = rospy.Publisher('/oculus', JointState, queue_size=10)
        #self.pub = rospy.Publisher('/dvrk_ecm/joint_states_robot', JointState, queue_size=10)

        self.bool = True 
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.ins  = 0
        self.sock = None
        self.data1= [0,0,0,0,0,0,0]
        self.data2= [0,0,0,0,0,0,0]
        self.CamBool = 0
        
            
    def Connection(self):
        
        self.sock = socket.create_connection(("172.21.38.35", 8888))
	print 'waiting'
        self.dataRec = self.sock.recv(150)
        self.dataRec = self.dataRec.replace(")(",",").replace(")","").replace("(","")
        self.dataRec = [float(num) for num in self.dataRec.split(',')]
        
    def Delta(self, data):
        
        self.yaw=  data.position[0] - self.dataRec[1]
        self.pitch= data.position[1]- self.dataRec[0] 
        self.ins=  data.position[2]- self.dataRec[6]
        self.roll=  data.position[3]- self.dataRec[2]
        
        self.data1=[-(self.dataRec[1]+self.yaw ), -(self.dataRec[0]+self.pitch) , (self.dataRec[6]+self.ins) , (self.dataRec[2]+self.roll)]       
        self.data2 = self.data1
        
        self.bool= False    
        
    def joints_limits(self):
        
        self.data1[0]=numpy.clip(self.data1[0],-0.4, 0.4)
        self.data1[1]=numpy.clip(self.data1[1],-0.4, 0.8)
        self.data1[3]=numpy.clip(self.data1[3],-0.8, 0.8)
        self.data1[2]=numpy.clip(self.data1[2],0, 0.21)  
        
    def steps(self):   
        
        #change the deltas 
        print "point3"
        if abs((self.dataRec[1] + self.yaw) - self.data2[0]) < 0.015 \
            and abs((self.dataRec[0] + self.pitch) - self.data2[1]) < 0.015 \
            and abs((self.dataRec[6] + self.ins) - self.data2[2]) < 0.0027 \
            and self.CamBool ==0 :
            #and abs((self.dataRec[2] + self.roll) - self.data2[3]) < 0.02 :
            
            self.data2[0] = self.dataRec[1] + self.yaw
            self.data2[1] = self.dataRec[0] + self.pitch
            self.data2[2] = self.dataRec[6] + self.ins
            self.data2[3] = self.dataRec[2] + self.roll
            
            #print self.data2[0]

        else:
            
            self.yaw = self.data2[0] - self.dataRec[1]
            self.pitch= self.data2[1] - self.dataRec[0]
            self.ins=  self.data2[2] - self.dataRec[6]
            #self.roll=  self.data2[3] - self.dataRec[2]
            
            #print self.data2[0]
            #print self.yaw
            
            
            
    def robPos(self, data):
        
        print data.position
    
       
    def publish_Data(self, data):
        
        
        if self.bool == True:
            
            self.Connection()

            self.Delta(data)

        try:     
            
            self.dataRec = self.sock.recv(150)
            #self.dataRec= (0.002, 0.139, -0.005, -0.990)(-0.033, -0.306, 0.196) 
            self.dataRec = self.dataRec.replace(")(",",").replace(")","").replace("(","")
            self.dataRec = [float(num) for num in self.dataRec.split(',')]
            self.steps()
              
            self.data1=[-(self.dataRec[1]+self.yaw ),- (self.dataRec[0]+self.pitch) , (self.dataRec[6]+self.ins) , (self.dataRec[2]+self.roll)]
            
            
            
            self.joints_limits()
            print >>sys.stderr, 'received "%s"' % self.data1

            self.joint_str=JointState()
            self.joint_str.name=['outer_yaw','outer_pitch','insertion','outer_roll']
            self.joint_str.position=self.data1
            
            
                
                
            self.pub.publish(self.joint_str)

        except:
        
            print >>sys.stderr, 'closing socket'
            self.sock.close()  
            
            try:        
                
                self.Connection()
                        
            except:              
                pass    
            
    def CamClutch(self, msg):
        
        self.CamBool = msg.buttons[0]
        print self.CamBool
            

    def listener(self):
        
        print 'running'
        rospy.init_node('joint_state_publisher')
        topic = '/oculus'  
        self.sub_pos = rospy.Subscriber('/dvrk/ECM/state_joint_current', JointState, self.publish_Data)     
        self.Cam_Clutch = rospy.Subscriber('/dvrk/footpedals/camera_minus', Joy, self.CamClutch )
        rospy.spin()
        
        
        
if __name__ == '__main__':
    
    try:
        
        st = main()
        st.__init__()
        st.joints_limits()
        st.listener()
        #publishData()

              
    except rospy.ROSInterruptException:
        pass    


    
    
    
    
