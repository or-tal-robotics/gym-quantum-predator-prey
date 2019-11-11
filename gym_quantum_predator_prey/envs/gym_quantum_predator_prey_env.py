import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from gym_quantum_predator_prey.envs.quantum_predator_prey import QPP
N_DISCRETE_ACTIONS = 6
PI = np.pi
HEIGHT, WIDTH, N_CHANNELS = 100, 100, 1


class QuantumPredatorPrey(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, mode):
        self.action_space = spaces.MultiDiscrete([N_DISCRETE_ACTIONS,N_DISCRETE_ACTIONS])
        self.observation_space = spaces.Box(low=0, high=255, shape=
                    (HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)
        
        self.done = False
        self.mode = mode
        self.QP = QuantumPong(mode = self.mode)
        self.MAX_STEPS = 20000
        self.step_count = 0
        
    def get_reward(self):
        reward = [0,0]
        if self.QP.ball_pos[1] > self.QP.bat_pos_B[1]:
            reward = [0,-1]
        if self.QP.ball_pos[1] < self.QP.bat_pos_A[1]:
            reward = [-1,0]   
        if self.QP.ball_pos[0] >= self.QP.bat_pos_A[0] - 5 and self.QP.ball_pos[0] <= self.QP.bat_pos_A[0] + 5 and self.QP.ball_pos[1] <= self.QP.bat_pos_A[1] :
            reward = [1,0]
        if self.QP.ball_pos[0] >= self.QP.bat_pos_B[0] - 5 and self.QP.ball_pos[0] <= self.QP.bat_pos_B[0] + 5 and self.QP.ball_pos[1] >= self.QP.bat_pos_B[1] :
            reward = [0,1]
        return reward
        

    def reset(self):
        self.QP = QuantumPong(mode = self.mode)
        self.QP._update_board()
        self.done = False
        self.reward = [0,0]
        self.step_count = 0
        return np.expand_dims(self.QP.board, axis=2).astype(np.uint8)
        
    def step(self, action):
        if self.done == True:
            self.__init__()
        reward = [0,0]
        score, observation, self.done, hit, win = self.QP.step(action[0], action[1])
        observation = np.expand_dims(observation, axis=2).astype(np.uint8)
        if hit == 1:
            reward = [1,0.1]
        if hit == -1:
           reward = [0.1,1]
        if win == 1:
           reward = [-0.1,-1]
        if win == -1:
           reward = [-1,-0.1]
           
        if action[0] == 0 or action[0] == 1:
            reward[0] -= 0.001
        if action[1] == 0 or action[1] == 1:
            reward[1] -= 0.001
            
        self.step_count += 1
        if self.step_count > self.MAX_STEPS:
            self.done = True
            print("Game over!, too many steps!")
        return observation, np.float32(reward), self.done, {}
    
#    def statistics(self):
#        M = np.array(self.QP.quantum_memory)
#        if M.shape[0] > 10:
#            C = np.empty((2,2))
#            C[0,0] = np.mean((M[:,0]==0)*(M[:,1]==0))
#            C[0,1] = np.mean((M[:,0]==0)*(M[:,1]==1))
#            C[1,0] = np.mean((M[:,0]==1)*(M[:,1]==0))
#            C[1,1] = np.mean((M[:,0]==1)*(M[:,1]==1))
#            qs = self.QP.QuantumState_memory
#            qst = self.QP.QuantumState_memory_total/self.step_count
#            return C, qs, qst
#        else:
#            return None, None, None
#    

         
    
       
       
        