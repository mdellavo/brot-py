import Numeric, pygame, pygame.surfarray, sys, time, math, multiprocessing
from multiprocessing import Process, Queue
from Queue import Empty
from pygame.locals import *

def generate_colormap(colors=256):
    start = 0x0000FF
    stop  = 0xFFFFFF
    step  = (stop-start)/colors
    return list(i for i in range(start, stop, step))

ln = math.log

def mandelbrot(width, height):

    iteration_limit = 256
    escape_radius   = 2
    colors          = generate_colormap()

    for h in height:
        line = []

        for w in width:
            
            iteration = 0

            x0 = float(w)/len(width)/2.0
            y0 = float(h)/len(height)/2.0

            x = 0.0
            y = 0.0
            
            def iter(x, y):                
                tmp = x**2 - y**2 + x0
                y   = 2.0 * x * y + y0
                x   = tmp
                
                return x, y

            while x**2 + y**2 <= escape_radius**2 and iteration<iteration_limit:
                tmp = x**2 - y**2 + x0
                y   = 2.0 * x * y + y0
                x   = tmp

                iteration += 1

            # FIXME
            for i in range(7):
                tmp = x**2 - y**2 + x0
                y   = 2.0 * x * y + y0
                x   = tmp

            # FIXME
            if iteration < iteration_limit:
                c     = iteration + ((ln(2.0 * ln(2.0)) - ln(ln(math.sqrt(x**2 + y**2))))/ln(2.0))
                idx   = int(round(math.log(abs(c), 2.0)/10.0 * 256.0))

                print idx

                if idx >= 256:
                    color = colors[-1]
                elif idx < 0:
                    color = colors[0]
                else:
                    coldor = colors[idx]
            else:
                color = 0
    
            line.append(color)

        yield (h, line)

def render(queue, width, height):
    for data in mandelbrot(width, height):
        queue.put([data])

    queue.put(None)
    queue.close()

def main(width, height, num_workers):
    
    pygame.init()
    pygame.display.set_caption('brot')
    clock   = pygame.time.Clock()
    screen  = pygame.display.set_mode((width, height), 0, 32)
    grid    = Numeric.zeros((width, height))
    workers = []

    for i in range(num_workers):
        queue         = Queue(height/num_workers)
        worker        = Process(target=render, args=(queue, range(width), range(i, height, num_workers)))
        worker.daemon = True
        worker.start()
        workers.append((queue, worker))
        print 'Spawned worker'

    while True:
        clock.tick(60)

        dirty = False

        for queue, worker in workers:
            if worker.is_alive():
                try:
                    for data in queue.get(False):

                        if data is not None:
                            row, line = data

                            # FIXME
                            for i, v in enumerate(line):
                                grid[i][row] = v

                            dirty = True
                        else:
                            worker.join()
                            print 'Worker Complete'

                except Empty, e:
                    pass

        if dirty:
            pygame.surfarray.blit_array(screen, grid)
            pygame.display.flip()
            dirty = False
                
        for e in pygame.event.get():
            if e.type == QUIT: 
                break
            elif e.type == KEYDOWN and e.key == K_q: 
                break
            elif e.type == KEYDOWN and e.key == K_s:
                filename = 'brot-%s.png' % time.strftime('%Y%m%d%H%M%S', time.localtime())
                pygame.image.save(screen, filename)
                print 'Saved %s' % filename

    for queue, worker in workers:
        worker.terminate()
        worker.join()

    pygame.display.quit()

if __name__ == '__main__':
    main(800, 600, multiprocessing.cpu_count())
