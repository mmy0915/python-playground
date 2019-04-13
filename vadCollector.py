import collections
import sys

"""
Frame类：存储帧的信息
timestamp:时间戳
duration:帧长
"""
class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

"""
音频分割成帧
"""
def frameGenerator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n

"""
按帧能量分割音频
"""
def vadCollector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames, start_speech, end_speech):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    for i, frame in enumerate(frames):
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                start_time = ring_buffer[0].timestamp
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                end_time = frame.timestamp + frame.duration
                end_speech.append(frame.timestamp + frame.duration)
                triggered = False
                yield [b''.join([f.bytes for f in voiced_frames]), start_time , end_time]
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
        end_speech.append(frame.timestamp + frame.duration)
        #start_speech.pop()
    sys.stdout.write('\n')
    if voiced_frames:
        yield [b''.join([f.bytes for f in voiced_frames]), start_time , end_time]
