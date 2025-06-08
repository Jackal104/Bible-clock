"""
Simple Amplified Bible data for demonstration.
This is a minimal implementation for the side-by-side display feature.
"""

# Sample Amplified Bible verses for demonstration
# In a full implementation, this would be loaded from a complete JSON file
AMPLIFIED_VERSES = {
    "Genesis": {
        1: {
            1: "In the beginning God (Elohim) created [by forming from nothing] the heavens and the earth."
        }
    },
    "John": {
        3: {
            16: "For God so [greatly] loved and dearly prized the world, that He [even] gave His [One and] only begotten Son, so that whoever believes and trusts in Him [as Savior] shall not perish, but have eternal life."
        },
        11: {
            17: "So when Jesus arrived, He found that Lazarus had already been in the tomb four days."
        }
    },
    "Psalms": {
        23: {
            1: "The Lord is my Shepherd [to feed, to guide and to shield me], I shall not want."
        }
    },
    "Matthew": {
        11: {
            17: "and say, 'We played the flute for you [pretending to be at a wedding], and you did not dance; we wailed sad dirges [pretending to be at a funeral], and you did not mourn and cry aloud.'"
        }
    },
    "Romans": {
        8: {
            28: "And we know [with great confidence] that God [who is deeply concerned about us] causes all things to work together [as a plan] for good for those who love God, to those who are called according to His plan and purpose."
        }
    },
    "1 Corinthians": {
        13: {
            4: "Love endures with patience and serenity, love is kind and thoughtful, and is not jealous or envious; love does not brag and is not proud or arrogant.",
            5: "It is not rude; it is not self-seeking, it is not provoked [nor overly sensitive and easily angered]; it does not take into account a wrong endured.",
            6: "It does not rejoice at injustice, but rejoices with the truth [when right and truth prevail].",
            7: "Love bears all things [regardless of what comes], believes all things [looking for the best in each one], hopes all things [remaining steadfast during difficult times], endures all things [without weakening].",
            8: "Love never fails [it never fades nor ends]. But as for prophecies, they will pass away; as for tongues, they will cease; as for the gift of special knowledge, it will pass away."
        }
    },
    "Hebrews": {
        11: {
            17: "By faith Abraham, when he was tested [that is, as the testing of his faith was still in progress], offered up Isaac, and he who had received the promises [of God] was ready to sacrifice his only son [of promise];"
        }
    },
    "Revelation": {
        21: {
            4: "and He will wipe away every tear from their eyes; and there will no longer be death; there will no longer be sorrow and anguish, or crying, or pain; for the former order of things has passed away."
        }
    }
}


def get_amplified_verse(book: str, chapter: int, verse: int) -> str:
    """
    Get an Amplified Bible verse.
    
    Args:
        book: Bible book name
        chapter: Chapter number
        verse: Verse number
        
    Returns:
        Amplified Bible verse text or None if not found
    """
    if book in AMPLIFIED_VERSES:
        if chapter in AMPLIFIED_VERSES[book]:
            if verse in AMPLIFIED_VERSES[book][chapter]:
                return AMPLIFIED_VERSES[book][chapter][verse]
    
    return None


def get_available_amplified_books() -> list:
    """Get list of books available in the Amplified sample."""
    return list(AMPLIFIED_VERSES.keys())


def has_amplified_verse(book: str, chapter: int, verse: int) -> bool:
    """Check if an Amplified verse exists for the given reference."""
    return get_amplified_verse(book, chapter, verse) is not None

