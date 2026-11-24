import sys, subprocess, os, importlib
anim = importlib.import_module(os.environ.get("ANIM", "anim"))
a, b, name = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
tmp = name + '.part.mp4'
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{anim.W}x{anim.H}',
                      '-r', str(anim.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17',
                      '-pix_fmt', 'yuv420p', '-f', 'mp4', tmp], stdin=subprocess.PIPE)
for i in range(round(a * anim.FPS), round(b * anim.FPS)):
    p.stdin.write(anim.frame(i / anim.FPS).tobytes())
p.stdin.close()
if p.wait() == 0: os.replace(tmp, name)
