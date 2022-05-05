import matplotlib.pyplot as plt
from matplotlib import animation
import math

plot_count=0
x=[]
y=[]

def draw_graph(i):
    global plot_count
    plot_count += 1
    if plot_count==20:
        exit()
    x.append(plot_count)
    y.append(math.log(plot_count))
    plt.cla()
    plt.plot(x,y)

anima= animation.FuncAnimation(plt.gcf(),draw_graph,interval=500)
plt.show()
