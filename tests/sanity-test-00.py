
import sys

import dr14meter.dr14_main as dr14


file = 'data/sample_audio_with_metadata.wav'


sys.argv = [__file__, 'data']
x = dr14.main()
print(x)

sys.argv = [__file__, '-f', file]
x = dr14.main()
print(x)

sys.argv = [__file__, '-1', '-f', file]
x = dr14.main()
print(x)

sys.argv = [__file__, '--hist', file]
x = dr14.main()
print(x)

sys.argv = [__file__, '--spectrogram', file]
x = dr14.main()
print(x)

sys.argv = [__file__, '--plot_track', file]
x = dr14.main()
print(x)

