import i8086EMU
import pyray as pr
import math

emulator = i8086EMU

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 320

SAMPLE_RATE = 44100
FREQ = 440
AMP = 0.085

phase = 0.0

@pr.ffi.callback("void(void *, unsigned int)")
def audio_callback(buffer_data, frames):
    global phase
    
    # Calculate how much the phase advances per sample based on the frequency and sample rate
    phase_increment = (FREQ / SAMPLE_RATE)
    
    # Create a buffer view to write directly to raylib's memory stream
    # Note: raylib audio expects 32-bit float audio for raw streams
    buffer = pr.ffi.cast("float *", buffer_data)
    
    for i in range(frames):
        # Generate the next sample in the sin wave
        #sawtooth
        sample = ((phase * 2.0) - 1.0) * AMP
        #sine wave
        #sample = math.sin(phase * math.tau) * AMP
        buffer[i] = sample
        
        # Advance and wrap the phase
        phase += phase_increment
        if phase >= 1.0:
            phase -= 1.0

def main():
    pr.init_window(WINDOW_WIDTH,WINDOW_HEIGHT, "CHIP-M8 EMULATOR")
    pr.init_audio_device()
    pr.set_window_icon(pr.Image())
    screen_pos = (int((pr.get_screen_width() + WINDOW_WIDTH)/2), int((pr.get_screen_height() + WINDOW_HEIGHT)/2))
    pr.set_window_position(*screen_pos)
    pr.set_target_fps(60)
    
    stream = pr.load_audio_stream(SAMPLE_RATE,32,1)
    pr.set_audio_stream_callback(stream,audio_callback)
    pr.play_audio_stream(stream)
    
    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)
        pr.draw_grid(20, 1.0)
        pr.draw_fps(20,20)
        pr.draw_rectangle(100,100,10,10,pr.RAYWHITE)
        pr.end_drawing()
        
    pr.stop_audio_stream(stream)
    pr.unload_audio_stream(stream)
    pr.close_audio_device()
    pr.close_window()

if __name__ == "__main__":
    main()