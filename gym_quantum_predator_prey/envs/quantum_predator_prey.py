import numpy as np
import time
import cv2

def sample_angle():
    d = np.random.binomial(1,0.5)
    theta = np.random.uniform(np.pi/12, np.pi - np.pi/12) * (-1)**d 
    return theta
    

class Player():
    def __init__(self, x, board_size, bat_size, dtheta = np.pi/12, dy = 3):
        self.x = x
        self.y = np.random.randint(bat_size+1, board_size[0] - bat_size-2)
        self.theta = np.random.uniform(0,2*np.pi)
        self.dy = dy
        self.dtheta = dtheta
        self.y_max = board_size[0]-bat_size-1
        self.y_min = bat_size
        self.score = 0
        self.theta_mesured = 0
        
    def update(self, action):
        if action == 0: # Move up
            self.y += self.dy
            if self.y > self.y_max:
                self.y = self.y_max
        elif action == 1: # Move down
            self.y -= self.dy
            if self.y < self.y_min:
                self.y = self.y_min
        elif action == 3: # Torret up
            self.theta += self.dtheta
        elif action == 4: # Torret up
            self.theta -= self.dtheta
            
class Ball():
    def __init__(self,x, y, V, theta):
        self.V = V
        self.x = x
        self.y = y
        self.theta = theta
        self.quantum_hits = 0
        self.polarization = np.random.uniform(0.0, np.pi)
        self.visible = 255
    



class QPP():
    def __init__(self, n_players = 1, board_size = (60,60,60), V = 2, n_rounds = 21, res = 0.2, mode="quantum"):
        self.bat_size = 6
        self.board_size = board_size
        self.board = np.zeros((int(board_size[0]/res),int(board_size[1]/res)))
        self.res = res
        self.ball = Ball(x = board_size[0]/2, y = board_size[1]/2, V = V, theta = sample_angle())
        self.mode = mode
        self.left_player = Player(6, board_size, self.bat_size)
        self.right_player = Player(board_size[1] - 6, board_size, self.bat_size)
        self.done = False
        self.n_rounds = n_rounds
        self.round = 0
        self.n_steps = 0
        self.board_angle = np.arctan((board_size[0]-board_size[2])/board_size[1])
        self.quantum_hits = 0
        

    
    def direction_probability(self, pose):
        if pose == 'left':
            t1 = np.remainder(self.left_player.theta,2*np.pi)
            t1 = np.min([t1, 2*np.pi-t1])
            t2 = np.remainder(self.ball.polarization,2*np.pi)
            t2 = np.min([t2, 2*np.pi-t2])
            x = np.abs(t1-t2)
            P = (1 + np.cos(2*x))/2
        elif pose == 'right':
            t1 = np.remainder(self.ball.polarization,2*np.pi)
            t1 = np.min([t1, 2*np.pi-t1])
            t2 = np.remainder(self.right_player.theta,2*np.pi)
            t2 = np.min([t2, 2*np.pi-t2])
            x = np.abs(t1-t2)
            P = (1 + np.cos(2*x))/2
            
        return P

    
        

    
    def _height(self,x):
        m = (self.board_size[2]-self.board_size[0])/self.board_size[1]
        b = self.board_size[0]
        h = x*m+b
        return h

        

        
    
    def _update_board(self):
        self.board = np.zeros((round(self.board_size[1]/self.res),round(self.board_size[0]/self.res)))
        Bx = int(round(self.ball.x/self.res))
        By = int(round(self.ball.y/self.res))
        cv2.circle(self.board,(By, Bx), 10, (self.ball.visible,self.ball.visible,self.ball.visible), -1)
        
        #self.board[50:-50,50:-50] = 0

        
        for ii in range(-round(self.bat_size/self.res),round(self.bat_size/self.res)+1):
            for jj in range(4):
                self.board[round(self.left_player.x/self.res)-jj, round(self.left_player.y/self.res)+ii-1] = 127
                self.board[round(self.right_player.x/self.res)+jj, round(self.right_player.y/self.res)+ii-1] = 127
#        
        for ii in range(round(self.board_size[1]/self.res)):
            self.board[ii, round(self._height(ii*self.res)/self.res)-3:round(self._height(ii*self.res)/self.res)-1] = 200
            self.board[ii,0:3] = 200
         
        
        x_tor = np.array([round(self.left_player.x/self.res), round(self.left_player.x/self.res) + (5/self.res)*np.sin((self.left_player.theta))]).astype(np.int)
        y_tor = np.array([round(self.left_player.y/self.res), round(self.left_player.y/self.res) + (5/self.res)*np.cos((self.left_player.theta))]) .astype(np.int)
        self.board = cv2.line(self.board,(y_tor[0],x_tor[0] ),(y_tor[1],x_tor[1] ),255,3)
        
       
        x_tor = np.array([round(self.right_player.x/self.res), round(self.right_player.x/self.res) + (5/self.res)*np.sin((self.right_player.theta))]).astype(np.int)
        y_tor = np.array([round(self.right_player.y/self.res), round(self.right_player.y/self.res) + (5/self.res)*np.cos((self.right_player.theta))]) .astype(np.int)
        self.board = cv2.line(self.board,(y_tor[0],x_tor[0] ),(y_tor[1],x_tor[1] ),255,3)
        
#        
        
                
                
    def step(self, Action_A, Action_B ):
        hit = 0
        win = 0
        # --- Player A --- #
        self.left_player.update(Action_A)
        
        
        # --- Player B --- #
        self.right_player.update(Action_B)
            
        # --- Ball step --- #
        self.ball.x +=  self.ball.V * np.cos(self.ball.theta)
        self.ball.y +=  self.ball.V * np.sin(self.ball.theta)
        self.ball.visible -= 20 
            
        # --- Ball --- #
        if self.ball.visible < 0:
            self.ball.visible = 0
            
        if self.ball.y > self._height(self.ball.x):
            self.ball.y = self._height(self.ball.x)
            self.ball.theta = - self.ball.theta - 2*self.board_angle
            
            
        if self.ball.y < 1:
            self.ball.y = 1
            self.ball.theta = - self.ball.theta
            
       
                        

        
        if self.ball.y >= self.left_player.y - self.bat_size and self.ball.y <= self.left_player.y + self.bat_size and self.ball.x <= self.left_player.x :
            self.ball.x = self.left_player.x
            hit = 1
            p = self.direction_probability("left")
            if np.random.binomial(1,p) == 1:
                self.ball.theta = np.pi - self.ball.theta
                self.ball.polarization = self.left_player.theta
            else:
                self.ball.theta = np.pi + self.ball.theta
                self.ball.polarization = self.left_player.theta + np.pi/2
                
        
                
        elif self.ball.x <= self.left_player.x and self.ball.x > self.left_player.x - 3:
            self.right_player.score += 1
            self.round += 1
            win = -1
            self.ball.visible = 255
            
        elif self.ball.x <= self.left_player.x - 3:
            self.ball.x = self.board_size[1]/2
            self.ball.y = self.board_size[0]/2
            self.ball.theta = sample_angle()
            self.ball.visible = 255
        
    
                
        if self.ball.y >= self.right_player.y - self.bat_size and self.ball.y <= self.right_player.y + self.bat_size and self.ball.x >= self.right_player.x :
            self.ball.x = self.right_player.x
            hit = -1
            p = self.direction_probability("right")
            if np.random.binomial(1,p) == 1:
                self.ball.theta = np.pi - self.ball.theta
                self.ball.polarization = self.right_player.theta
            else:
                self.ball.theta = np.pi + self.ball.theta
                self.ball.polarization = self.right_player.theta + np.pi/2
                
           
        elif self.ball.x >= self.right_player.x and self.ball.x < self.right_player.x + 3:
            self.left_player.score += 1
            self.round += 1
            win = 1
            self.ball.visible = 255
            
        elif self.ball.x >= self.right_player.x + 3:
            self.ball.x = self.board_size[1]/2
            self.ball.y = self.board_size[0]/2
            self.ball.theta = sample_angle()
            self.ball.visible = 255
                
        
        if self.round == 21:
            self.done = True
            self.n_steps = 0
                
        self.n_steps += 1
        self._update_board()
        return [self.left_player.score, self.right_player.score], self.board, self.done, hit, win
    
    
if __name__ == '__main__':

    QP = QuantumPong()
    done = False
    steps = 0
    while not done:
        a = QP.step(3,4)
        done = a[2]
        cv2.imshow("video",a[1]/255)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        
        
                
                
                
                
        