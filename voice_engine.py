"""
voice_engine.py
Modern Standard Arabic Voice Engine for XO (Tic-Tac-Toe).
Plays dignified, articulate, studio-quality Arabic speech recordings completely OFFLINE!
Uses Windows Multimedia API (mciSendString) for instantaneous, zero-lag playback.
"""

import ctypes
import os
import random
import threading
from typing import Callable, Optional

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
TTS_AVAILABLE = True


class AIVoiceEngine:
    """Manages articulate Modern Standard Arabic voice playback and speech bubble updates."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.last_comment: str = "مرحباً بك، أتمنى لك جولة ممتعة وحظاً موفقاً."
        self._lock = threading.Lock()

        # Modern Standard Arabic Lines with corresponding MP3 audio files
        self.audio_start = [
            ("مرحباً بك، ابدأ أنت أولاً، وأتمنى لك جولة موفقة وممتعة.", "start_1.mp3"),
            ("أهلاً بك يا صديقي، تفضل بالخطوة الأولى، ولنبدأ التحدي.", "start_2.mp3"),
            ("الميدان لك، خذ وقتك في التفكير وابدأ بحركتك الافتتاحية.", "start_3.mp3"),
        ]

        self.audio_start_ai = [
            ("سأبدأ أنا هذه الجولة، راقب خطوتي الافتتاحية بدقة.", "start_ai_1.mp3"),
            ("بداية الجولة من جانبي، استعد لخوض هذا النزال.", "start_ai_2.mp3"),
        ]

        self.audio_moves = {
            0: ("اخترت الزاوية العليا، والآن دورك لتتحرك.", "move_0.mp3"),
            1: ("وضعت علامتي في المنتصف العلوي، فكّر في خطوتك القادمة.", "move_1.mp3"),
            2: ("أحكمت السيطرة على هذا الركن، بانتظار ردك.", "move_2.mp3"),
            3: ("تحركت إلى الجانب الأيسر، ركّز جيداً على اللوحة.", "move_3.mp3"),
            4: ("استحوذت على خانة المنتصف، فهي مفتاح السيطرة على الرقعة.", "move_4.mp3"),
            5: ("أغلقت هذا الجانب، إلى أين ستتجه الآن؟", "move_5.mp3"),
            6: ("الركن السفلي تحت سيطرتي، خطط لحركتك بعناية.", "move_6.mp3"),
            7: ("تحركت إلى المنتصف السفلي، الدور لك الآن.", "move_7.mp3"),
            8: ("شغلت هذه الزاوية، والنزال يزداد إثارة.", "move_8.mp3"),
        }

        self.audio_threat = [
            ("احذر، فأنا على بعد خطوة واحدة فقط من حسم النتيجة!", "threat_1.mp3"),
            ("انتبه جيداً لمواقع قطعك، فقد تركت مساراً خطيراً مكشوفاً!", "threat_2.mp3"),
            ("ركز في دفاعك، فالفرصة باتت مواتية لإنهاء الجولة لصالحي!", "threat_3.mp3"),
        ]

        self.audio_win_ai = [
            ("مباراة رائعة وتحدٍ مميز، حظاً أوفر في الجولة القادمة.", "win_ai_1.mp3"),
            ("انتهت الجولة بفوزي، أشكرك على هذا التنافس الجميل.", "win_ai_2.mp3"),
        ]

        self.audio_win_human = [
            ("أحسنت صنعاً! لقد كانت خطة محكمة واستحققت الفوز بجدارة، مبارك لك.", "win_human.mp3"),
        ]

        self.audio_draw = [
            ("تعادل مستحق، كان أداؤك الدفاعي ممتازاً طوال الجولة.", "draw_1.mp3"),
            ("انتهت الجولة بالتعادل، لعب متكافئ ودقيق من الطرفين.", "draw_2.mp3"),
        ]

    def _play_mp3_async(self, mp3_filename: str):
        """Plays the Arabic MP3 in a background thread."""
        if not self.enabled:
            return

        mp3_path = os.path.join(AUDIO_DIR, mp3_filename)
        if not os.path.exists(mp3_path):
            return

        def _worker():
            with self._lock:
                try:
                    alias = f"ai_voice_{random.randint(100, 999)}"
                    # Stop any previous playback
                    ctypes.windll.winmm.mciSendStringW('close all', None, 0, None)
                    # Open and play MP3 via Windows Multimedia API
                    ctypes.windll.winmm.mciSendStringW(f'open "{mp3_path}" type mpegvideo alias {alias}', None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                except Exception as e:
                    print(f"Audio Playback Notice: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def play_phrase(self, text_arabic: str, mp3_name: str, on_text_spoken: Optional[Callable[[str], None]] = None):
        """Updates UI with Arabic text and plays native audio."""
        self.last_comment = text_arabic
        if on_text_spoken:
            on_text_spoken(text_arabic)
        self._play_mp3_async(mp3_name)

    def comment_game_start(self, ai_starts: bool = False, on_text_spoken: Optional[Callable[[str], None]] = None):
        choices = self.audio_start_ai if ai_starts else self.audio_start
        txt, mp3 = random.choice(choices)
        self.play_phrase(txt, mp3, on_text_spoken)

    def comment_ai_move(self, cell_idx: int, nodes: int, is_threat: bool = False, on_text_spoken: Optional[Callable[[str], None]] = None):
        if is_threat:
            txt, mp3 = random.choice(self.audio_threat)
        else:
            default_txt = f"تحركت إلى الخانة رقم {cell_idx}، بانتظار دورك."
            txt, mp3 = self.audio_moves.get(cell_idx, (default_txt, f"move_{cell_idx}.mp3"))
        self.play_phrase(txt, mp3, on_text_spoken)

    def comment_game_over(self, winner: Optional[str], on_text_spoken: Optional[Callable[[str], None]] = None):
        if winner == "AI":
            txt, mp3 = random.choice(self.audio_win_ai)
        elif winner == "Human":
            txt, mp3 = random.choice(self.audio_win_human)
        else:
            txt, mp3 = random.choice(self.audio_draw)
        self.play_phrase(txt, mp3, on_text_spoken)
