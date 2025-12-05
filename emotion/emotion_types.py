"""
Emotion Types
Defines all possible emotion states for chess pieces
"""

from enum import Enum


class Emotion(Enum):
    """Enumeration of all possible emotions"""

    HAPPY = "HAPPY"
    SAD = "SAD"
    SCARED = "SCARED"
    CONFIDENT = "CONFIDENT"
    ANGRY = "ANGRY"
    NEUTRAL = "NEUTRAL"
    ANXIOUS = "ANXIOUS"
    PROUD = "PROUD"
    RESIGNED = "RESIGNED"
    EXCITED = "EXCITED"
    DETERMINED = "DETERMINED"
    HOPEFUL = "HOPEFUL"
    DESPERATE = "DESPERATE"

    def get_emoji(self) -> str:
        """Get emoji representation"""
        emoji_map = {
            Emotion.HAPPY: '😊',
            Emotion.SAD: '😢',
            Emotion.SCARED: '😰',
            Emotion.CONFIDENT: '😤',
            Emotion.ANGRY: '😠',
            Emotion.NEUTRAL: '😐',
            Emotion.ANXIOUS: '😟',
            Emotion.PROUD: '😎',
            Emotion.RESIGNED: '😔',
            Emotion.EXCITED: '🤩',
            Emotion.DETERMINED: '😠',
            Emotion.HOPEFUL: '🙂',
            Emotion.DESPERATE: '😭'
        }
        return emoji_map.get(self, '😐')

    def get_intensity(self) -> int:
        """Get emotion intensity (1-10)"""
        intensity_map = {
            Emotion.HAPPY: 7,
            Emotion.SAD: 6,
            Emotion.SCARED: 9,
            Emotion.CONFIDENT: 8,
            Emotion.ANGRY: 8,
            Emotion.NEUTRAL: 1,
            Emotion.ANXIOUS: 7,
            Emotion.PROUD: 8,
            Emotion.RESIGNED: 5,
            Emotion.EXCITED: 9,
            Emotion.DETERMINED: 9,
            Emotion.HOPEFUL: 6,
            Emotion.DESPERATE: 10
        }
        return intensity_map.get(self, 5)

    def is_positive(self) -> bool:
        """Check if emotion is positive"""
        positive = {Emotion.HAPPY, Emotion.CONFIDENT, Emotion.PROUD,
                    Emotion.EXCITED, Emotion.DETERMINED, Emotion.HOPEFUL}
        return self in positive

    def is_negative(self) -> bool:
        """Check if emotion is negative"""
        negative = {Emotion.SAD, Emotion.SCARED, Emotion.ANGRY,
                    Emotion.ANXIOUS, Emotion.RESIGNED, Emotion.DESPERATE}
        return self in negative

    @classmethod
    def from_string(cls, emotion_str: str):
        """Create Emotion from string"""
        try:
            return cls[emotion_str.upper()]
        except KeyError:
            return cls.NEUTRAL


class EmotionContext:
    """Context for determining emotions based on game situations"""

    # Situation to emotion mappings
    UNDER_ATTACK = {
        'high_value': Emotion.SCARED,
        'low_value': Emotion.ANXIOUS,
        'defended': Emotion.CONFIDENT
    }

    CAPTURE = {
        'high_value': Emotion.PROUD,
        'equal_trade': Emotion.CONFIDENT,
        'bad_trade': Emotion.RESIGNED
    }

    SUPPORT = {
        'protecting': Emotion.DETERMINED,
        'being_protected': Emotion.HOPEFUL,
        'coordinated': Emotion.CONFIDENT
    }

    ISOLATION = {
        'alone': Emotion.ANXIOUS,
        'surrounded': Emotion.DESPERATE,
        'advancing': Emotion.CONFIDENT
    }

    SACRIFICE = {
        'willing': Emotion.RESIGNED,
        'forced': Emotion.DESPERATE,
        'heroic': Emotion.PROUD
    }

    VICTORY = {
        'winning': Emotion.HAPPY,
        'dominating': Emotion.EXCITED,
        'close': Emotion.DETERMINED
    }

    DEFEAT = {
        'losing': Emotion.SAD,
        'hopeless': Emotion.RESIGNED,
        'fighting': Emotion.DETERMINED
    }

    @staticmethod
    def get_emotion_for_situation(situation: str, context: str = None):
        """
        Get appropriate emotion for a situation

        Args:
            situation: Main situation type
            context: Optional context within situation

        Returns:
            Emotion enum value
        """
        situation_map = {
            'under_attack': EmotionContext.UNDER_ATTACK,
            'capture': EmotionContext.CAPTURE,
            'support': EmotionContext.SUPPORT,
            'isolation': EmotionContext.ISOLATION,
            'sacrifice': EmotionContext.SACRIFICE,
            'victory': EmotionContext.VICTORY,
            'defeat': EmotionContext.DEFEAT
        }

        situation_emotions = situation_map.get(situation, {})

        if context and context in situation_emotions:
            return situation_emotions[context]

        # Return first emotion in situation or neutral
        return list(situation_emotions.values())[0] if situation_emotions else Emotion.NEUTRAL