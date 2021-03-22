from tkinter import *
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter

root = Tk()
root.geometry('1200x700+200+100')
root.title('This is my root window')
root.state('zoomed')
root.config(background='#fafafa')

xar = []
yar = []


def animate(i):
    #ser.reset_input_buffer()
    #data = ser.readline().decode("utf-8")
    #data_array = data.split(',')
    #yvalue = float(data_array[1])
    yar.append(99-i)
    xar.append(i)
    line.set_data(xar, yar)

    ax1.set_xlim(0, i+1)
    print(i)

# style.use('ggplot')
# fig = plt.figure(figsize=(14, 4.5), dpi=100)

# ax1 = fig.add_subplot(1, 1, 1)
# ax1.set_ylim(0, 100)
# line, = ax1.plot(xar, yar, 'r', marker='o')




outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')
plt.style.use("seaborn-darkgrid")
f = plt.figure(1,figsize=(10,8))
f.canvas.set_window_title('SPREAD MONITOR')
min_form = DateFormatter("%H:%M")
sec_form = DateFormatter("%M:%S")
gs = f.add_gridspec(5, 3)

a=[1,2,1]
b=[1,2,3]

#set the self plot


# m2 = f.add_subplot(gs[4,:])
# m2.tick_params(axis='both', which='major', labelsize=8)
# m2.set_title('5 min Spread')

m_dis,w_dis,roc1l,roc5l,roc15l = a,a,a,a,a
#m_dis,w_dis,roc1l,roc5l,roc15l = SVF.find_info(symbols)

outlier = dict(linewidth=3, color='darkgoldenrod',marker='o')
plt.style.use("seaborn-darkgrid")
f = plt.figure(1,figsize=(8,8))
f.canvas.set_window_title('SPREAD MONITOR')
min_form = DateFormatter("%H:%M")
sec_form = DateFormatter("%M:%S")
spread = f.add_subplot(gs[0,:])
spread.tick_params(axis='both', which='major', labelsize=8)
spread.set_title('IntraDay Spread')

m1 = f.add_subplot(gs[3,:])
m1.tick_params(axis='both', which='major', labelsize=8)
m1.set_title('1 min Spread')

max_spread_d = f.add_subplot(gs[1,0])
max_spread_d.set_title('Max Spread Today')
max_spread_d.boxplot([], flierprops=outlier,vert=False, whis=1)

max_spread_w = f.add_subplot(gs[1,1])
max_spread_w.set_title('Max Spread Weekly')
max_spread_w.boxplot(w_dis, flierprops=outlier,vert=False, whis=1)

max_spread_m = f.add_subplot(gs[1,2])
max_spread_m.set_title('Max Spread Monthly')
max_spread_m.boxplot(m_dis, flierprops=outlier,vert=False, whis=1)


roc1 = f.add_subplot(gs[2,0])
roc1.set_title('Speed 1 min')
roc1.boxplot(roc1l, flierprops=outlier,vert=False, whis=2.5)

roc5 = f.add_subplot(gs[2,1])
roc5.set_title('Speed 5 min')
roc5.boxplot(roc5l, flierprops=outlier,vert=False, whis=1.5)

roc15 =f.add_subplot(gs[2,2])
roc15.set_title('Speed 15 min')
roc15.boxplot(roc15l, flierprops=outlier,vert=False, whis=1.5)
plt.tight_layout()

plotcanvas = FigureCanvasTkAgg(f, root)
plotcanvas.get_tk_widget().grid(column=1, row=1)


#ani = animation.FuncAnimation(fig, animate, interval=1000, blit=False)

root.mainloop()