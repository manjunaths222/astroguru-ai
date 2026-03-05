"""Seed script to populate articles table with sample Vedic Astrology content"""

import os
import sys
from datetime import datetime
import psycopg2

# Add project root to path and load .env
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

# Get database URL from environment
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/astroguru_db"
)

# Convert async URL to sync URL if needed
if "postgresql+asyncpg://" in database_url:
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

# Sample articles about Vedic Astrology
SAMPLE_ARTICLES = [
    (
        "Introduction to Vedic Astrology: Ancient Wisdom for Modern Times",
        "introduction-vedic-astrology",
        "Discover the foundations of Vedic Astrology, one of the oldest and most accurate systems of astrology known to humanity.",
        "Basics",
        "AstroGuru Team",
        "https://images.unsplash.com/photo-1545457521-b00b0e90d453?w=800&h=400&fit=crop",
        """# Introduction to Vedic Astrology: Ancient Wisdom for Modern Times

Vedic Astrology, also known as Jyotisha, is an ancient Indian system of astrology that has been practiced for thousands of years. Unlike Western astrology, Vedic astrology focuses on the sidereal zodiac and provides deep insights into your life's purpose, personality, and future.

## What Makes Vedic Astrology Different?

Vedic Astrology uses the sidereal zodiac, which is based on the actual star positions at the time of your birth. This is different from Western astrology which uses the tropical zodiac. The sidereal zodiac is more accurate and provides a more realistic representation of the planetary positions at the time of your birth.

## The Nine Planets (Navagrahas)

In Vedic Astrology, the nine planets are:
- **Sun (Surya)** - Represents your core essence and life purpose
- **Moon (Chandra)** - Represents your emotions and inner peace
- **Mars (Mangal)** - Represents your courage and energy
- **Mercury (Budh)** - Represents your intelligence and communication
- **Jupiter (Guru)** - Represents your expansion and wisdom
- **Venus (Shukra)** - Represents your love and beauty
- **Saturn (Shani)** - Represents your discipline and karmic lessons
- **Rahu** - Represents your desires and obsessions
- **Ketu** - Represents your spiritual insights and detachment

## The Twelve Zodiac Signs (Rashis)

Each zodiac sign in Vedic Astrology has unique characteristics and is ruled by a different planet. Your sun sign (Rashi) is determined by the position of the Sun at the time of your birth.

## Why Consult with a Vedic Astrologer?

A Vedic astrologer can help you understand your birth chart (Janam Kundli), identify auspicious times for important decisions, and guide you through life's challenges. Whether you're facing career dilemmas, relationship issues, or simply seeking spiritual guidance, Vedic Astrology offers profound insights.

Start your journey with AstroGuru AI today and discover your cosmic destiny!""",
    ),
    (
        "Understanding Your Birth Chart (Janam Kundli)",
        "understanding-birth-chart",
        "Learn how to read and interpret your Vedic birth chart to unlock the secrets of your destiny.",
        "Birth Chart",
        "Dr. Rajesh Sharma",
        "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=800&h=400&fit=crop",
        """# Understanding Your Birth Chart (Janam Kundli)

Your birth chart, known as Janam Kundli in Vedic Astrology, is a snapshot of the planetary positions at the exact moment, date, and location of your birth. It's like a cosmic fingerprint that reveals your personality, life purpose, and destiny.

## What Information Do You Need?

To create an accurate Janam Kundli, you'll need:
1. **Date of Birth** - The exact date you were born
2. **Time of Birth** - As precise as possible (accurate to the minute)
3. **Place of Birth** - The city and country where you were born

## The Twelve Houses (Bhavas)

Your birth chart is divided into 12 houses, each representing different areas of your life:

- **1st House** - Self, personality, physical appearance
- **2nd House** - Wealth, finances, family
- **3rd House** - Communication, siblings, short journeys
- **4th House** - Home, property, mother, peace of mind
- **5th House** - Children, creativity, romance, intelligence
- **6th House** - Health, enemies, debts, day-to-day work
- **7th House** - Marriage, partnerships, business
- **8th House** - Inheritance, transformation, occult knowledge
- **9th House** - Father, spirituality, luck, long journeys
- **10th House** - Career, social status, public life
- **11th House** - Friendships, gains, aspirations
- **12th House** - Loss, expenses, isolation, spiritual liberation

## How to Interpret Your Chart

The interpretation of your birth chart involves understanding:
- The sign (Rashi) in each house
- The planets placed in each house
- The aspects between planets
- The strength and weakness of each planet

## Get Your Birth Chart Analyzed

With AstroGuru AI, you can upload your birth details and receive a detailed analysis of your Janam Kundli, including insights about your personality, career, relationships, and spiritual path.""",
    ),
    (
        "The Twelve Zodiac Signs in Vedic Astrology (Rashis)",
        "twelve-zodiac-signs",
        "Explore the characteristics and traits of each Vedic zodiac sign and what they reveal about your personality.",
        "Rashis",
        "AstroGuru Team",
        "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=800&h=400&fit=crop",
        """# The Twelve Zodiac Signs in Vedic Astrology (Rashis)

In Vedic Astrology, there are twelve zodiac signs, each with unique characteristics, ruling planets, and symbolic representations. Your Sun sign (Rashi) is determined by the position of the Sun at the time of your birth.

## The Twelve Rashis

### 1. Aries (Mesha) - March 21 to April 19
Ruled by Mars, Aries natives are courageous, adventurous, and passionate. They're natural leaders with a strong drive to succeed.

### 2. Taurus (Vrishabha) - April 20 to May 20
Ruled by Venus, Taurus natives are stable, reliable, and sensual. They appreciate the finer things in life and value security.

### 3. Gemini (Mithuna) - May 21 to June 20
Ruled by Mercury, Gemini natives are intelligent, communicative, and versatile. They love learning and exploring new ideas.

### 4. Cancer (Karka) - June 21 to July 22
Ruled by the Moon, Cancer natives are emotional, nurturing, and intuitive. They're deeply connected to their family and roots.

### 5. Leo (Simha) - July 23 to August 22
Ruled by the Sun, Leo natives are confident, creative, and charismatic. They love being in the spotlight and inspiring others.

### 6. Virgo (Kanya) - August 23 to September 22
Ruled by Mercury, Virgo natives are analytical, practical, and detail-oriented. They strive for perfection in all they do.

### 7. Libra (Tula) - September 23 to October 22
Ruled by Venus, Libra natives are balanced, diplomatic, and artistic. They seek harmony in all relationships and situations.

### 8. Scorpio (Vrishchika) - October 23 to November 21
Ruled by Mars (and Pluto in modern astrology), Scorpio natives are intense, mysterious, and transformative. They're deeply intuitive and powerful.

### 9. Sagittarius (Dhanu) - November 22 to December 21
Ruled by Jupiter, Sagittarius natives are adventurous, optimistic, and philosophical. They're seekers of truth and wisdom.

### 10. Capricorn (Makara) - December 22 to January 19
Ruled by Saturn, Capricorn natives are disciplined, ambitious, and responsible. They climb the mountain of success with determination.

### 11. Aquarius (Kumbha) - January 20 to February 18
Ruled by Saturn (and Uranus in modern astrology), Aquarius natives are innovative, humanitarian, and independent. They're visionaries of the future.

### 12. Pisces (Meena) - February 19 to March 20
Ruled by Jupiter, Pisces natives are compassionate, artistic, and spiritual. They're dreamers who connect with the invisible realms.

## Find Your Rashi

Discover which Rashi you belong to and unlock deeper insights into your personality, strengths, and challenges with AstroGuru AI.""",
    ),
    (
        "Planetary Dashas: Understanding Your Life Timeline",
        "planetary-dashas",
        "Explore the concept of Dashas in Vedic Astrology and how they reveal the timeline of your life.",
        "Advanced",
        "Pt. Arun Bansal",
        "https://images.unsplash.com/photo-1444080748397-f442aa95c3e5?w=800&h=400&fit=crop",
        """# Planetary Dashas: Understanding Your Life Timeline

In Vedic Astrology, Dasha systems are one of the most important predictive tools. A Dasha is a period during which a particular planet has significant influence on your life. Understanding your Dasha timeline can help you navigate life's challenges and opportunities.

## What Are Dashas?

Dashas are planetary periods that determine the timing of events in your life. They're calculated based on the position of the Moon at the time of your birth. Each Dasha lasts for a specific number of years, and during this period, that planet influences various aspects of your life.

## The Main Dasha System: Vimshottari Dasha

The most commonly used Dasha system is the Vimshottari Dasha, which has a total cycle of 120 years. The sequence of planets in Vimshottari Dasha is:

1. **Ketu** - 7 years
2. **Venus** - 20 years
3. **Sun** - 6 years
4. **Moon** - 10 years
5. **Mars** - 7 years
6. **Rahu** - 18 years
7. **Jupiter** - 16 years
8. **Saturn** - 19 years
9. **Mercury** - 17 years

## Sub-Dashas (Bhuktis)

Each main Dasha is further divided into sub-periods called Bhuktis. These Bhuktis provide more detailed insights into specific events during a Dasha period.

## How Dashas Affect Your Life

During a favorable Dasha:
- You may experience growth, success, and positive changes
- New opportunities and relationships may come into your life
- Your overall well-being and happiness increase

During a challenging Dasha:
- You may face obstacles, delays, and difficult situations
- You should exercise caution in important decisions
- This is a time to build strength and resilience

## Remedies During Challenging Dashas

If you're going through a challenging Dasha, Vedic Astrology suggests:
- Wearing gemstones associated with favorable planets
- Performing rituals and prayers
- Practicing meditation and yoga
- Seeking guidance from an experienced astrologer

Get a detailed Dasha analysis with AstroGuru AI and plan your life accordingly!""",
    ),
    (
        "Remedies in Vedic Astrology: Gemstones, Mantras, and Rituals",
        "vedic-astrology-remedies",
        "Discover the powerful remedies in Vedic Astrology to mitigate planetary challenges and enhance positive influences.",
        "Remedies",
        "Swami Anand Nath",
        "https://images.unsplash.com/photo-1516714712202-4e88e84fbf6c?w=800&h=400&fit=crop",
        """# Remedies in Vedic Astrology: Gemstones, Mantras, and Rituals

Vedic Astrology doesn't just predict your future—it also offers remedies to mitigate challenging planetary influences and enhance positive ones. These remedies have been used for centuries to transform lives.

## The Power of Gemstones (Ratnas)

Gemstones are one of the most popular remedies in Vedic Astrology. Each planet is associated with specific gemstones:

- **Sun** - Ruby (Manik)
- **Moon** - Pearl (Moti)
- **Mars** - Red Coral (Moonga)
- **Mercury** - Emerald (Panna)
- **Jupiter** - Yellow Sapphire (Pukhraj)
- **Venus** - Diamond (Heera)
- **Saturn** - Blue Sapphire (Neelam)
- **Rahu** - Hessonite (Gomedh)
- **Ketu** - Agate (Vaidurya)

## The Importance of Proper Gemstone Selection

It's crucial to:
- Consult an astrologer to determine which gemstones are suitable for you
- Ensure the gemstone is authentic and of good quality
- Have the gemstone properly energized before wearing
- Wear the gemstone on the correct finger and day

## The Power of Mantras

Reciting mantras associated with planets can help reduce negative effects:

- **Surya Mantra** (Sun): "Om Suryaya Namah"
- **Chandra Mantra** (Moon): "Om Chandraya Namah"
- **Mangal Mantra** (Mars): "Om Angarakaya Namah"
- **Budh Mantra** (Mercury): "Om Budhaya Namah"
- **Guru Mantra** (Jupiter): "Om Brihaspataye Namah"
- **Shukra Mantra** (Venus): "Om Shukraya Namah"
- **Shani Mantra** (Saturn): "Om Shanaye Namah"

## Rituals and Practices

Other effective remedies include:
- **Yajnas** - Vedic fire rituals performed by priests
- **Charity** - Donating to those in need
- **Fasting** - Observing fasts on specific days
- **Yoga and Meditation** - Balancing mind and body
- **Puja** - Performing worship rituals

## The Science Behind Remedies

These remedies work by:
- Aligning your energy with the cosmic vibrations
- Reducing the negative effects of malefic planets
- Strengthening the positive influences in your chart
- Promoting inner peace and spiritual growth

Explore personalized remedies for your unique birth chart with AstroGuru AI!""",
    ),
    (
        "Career and Finance: What Your Birth Chart Reveals",
        "career-finance-astrology",
        "Learn how to use your Vedic birth chart to guide your career decisions and improve your financial prospects.",
        "Career",
        "Rajiv Chopra",
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=400&fit=crop",
        """# Career and Finance: What Your Birth Chart Reveals

Your Vedic birth chart contains valuable insights into your career potential, financial prospects, and the best paths for success. By understanding these planetary influences, you can make informed decisions about your professional life.

## The Houses of Career and Finance

### 10th House - Career and Public Life
The 10th house represents your career, professional reputation, and social status. The planet ruling this house and its position indicate your career potential and the types of professions that suit you.

### 11th House - Income and Gains
The 11th house governs income from profession, business gains, and financial growth. A strong 11th house indicates financial success and abundance.

### 2nd House - Wealth and Resources
The 2nd house represents accumulated wealth, family resources, and financial stability. Its condition reveals your relationship with money.

## Planets and Career

- **Sun** - Leadership roles, government jobs, administration
- **Moon** - Tourism, hospitality, creative fields, nursing
- **Mars** - Military, police, engineering, sports
- **Mercury** - Communication, teaching, writing, business
- **Jupiter** - Law, religion, higher education, finance
- **Venus** - Entertainment, arts, fashion, luxury goods
- **Saturn** - Agriculture, mining, construction, hard work

## Favorable Periods for Career Changes

Your Dasha timeline reveals the most auspicious periods for:
- Changing jobs or starting a business
- Taking on new responsibilities
- Launching a new venture
- Seeking promotion or recognition

## Financial Remedies

If your chart shows financial challenges:
- Wear recommended gemstones
- Recite prosperity mantras daily
- Practice charity and give to those in need
- Invest during favorable planetary periods
- Follow your astrologer's guidance on auspicious days

## Timing Your Decisions

By understanding your birth chart and Dasha timeline, you can:
- Choose the best time to launch a business
- Make investments during favorable periods
- Plan major financial decisions
- Avoid making important decisions during challenging periods

Unlock your financial potential with a detailed career and finance analysis from AstroGuru AI!""",
    ),
    (
        "Mangal Dosha: Understanding Mars in Indian Marriage Astrology",
        "mangal-dosha-indian-marriage",
        "Mangal Dosha is a crucial factor in Indian matchmaking. Learn how Mars placement affects marriage compatibility in Vedic astrology.",
        "Marriage",
        "Pt. Arun Bansal",
        "https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800&h=400&fit=crop",
        """# Mangal Dosha: Understanding Mars in Indian Marriage Astrology

Mangal Dosha, or Kuja Dosha, is one of the most discussed topics in Indian Vedic astrology, especially when it comes to marriage compatibility. In India, astrologers carefully analyze birth charts before finalizing marriages.

## What is Mangal Dosha?

Mangal Dosha occurs when Mars (Mangal) is placed in the 1st, 2nd, 4th, 7th, 8th, or 12th house of the birth chart. Mars is considered a malefic planet in these positions for marriage and can create challenges in marital life.

## Why It Matters in Indian Weddings

In traditional Indian matchmaking (Kundli Milan), Mangal Dosha is given significant weight. Families often consult astrologers to check compatibility, and Mangal Dosha can be a deciding factor in marriage proposals.

## Remedies for Mangal Dosha

- **Mangalik Dosha Nivaran Puja** - Special rituals performed before marriage
- **Kumbh Vivah** - Symbolic marriage to a banana tree or clay pot
- **Wearing Red Coral (Moonga)** - After astrologer consultation
- **Chanting Hanuman Chalisa** - Mars is associated with Hanuman
- **Fasting on Tuesdays** - Mars' day

## Cancellation of Mangal Dosha

Mangal Dosha can be cancelled or neutralized when both partners have it—this is called "Dosha Nash" or Dosha cancellation. The severity also varies based on the house placement.

Get your compatibility analysis with AstroGuru AI!""",
    ),
    (
        "Nakshatras: The 27 Lunar Mansions of Vedic Astrology",
        "nakshatras-lunar-mansions",
        "Nakshatras are the 27 lunar mansions that form the foundation of Vedic astrology. Discover their significance in Indian astrological practice.",
        "Nakshatras",
        "Dr. Rajesh Sharma",
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&h=400&fit=crop",
        """# Nakshatras: The 27 Lunar Mansions of Vedic Astrology

Nakshatras are a unique feature of Vedic astrology, dividing the zodiac into 27 equal parts of 13°20' each. Each Nakshatra has its own deity, symbol, and characteristics that influence your personality and destiny.

## The 27 Nakshatras

1. **Ashwini** - Horse head, ruled by Ketu
2. **Bharani** - Yoni, ruled by Venus
3. **Krittika** - Knife, ruled by Sun
4. **Rohini** - Cart, ruled by Moon
5. **Mrigashira** - Deer head, ruled by Mars
6. **Ardra** - Teardrop, ruled by Rahu
7. **Punarvasu** - Bow, ruled by Jupiter
8. **Pushya** - Cow's udder, ruled by Saturn
9. **Ashlesha** - Serpent, ruled by Mercury
10. **Magha** - Throne, ruled by Ketu
... and 17 more through Revati

## Nakshatra in Indian Culture

In India, the birth Nakshatra (Janma Nakshatra) is used for naming ceremonies, Muhurta selection, and understanding one's inherent nature. Many Indian parents name their children based on the birth Nakshatra's starting syllable.

## Nakshatra and Marriage

Nakshatra compatibility (Nadi Dosha) is crucial in Indian matchmaking. Certain Nakshatra combinations are considered inauspicious and are avoided in arranged marriages.

Discover your Nakshatra with AstroGuru AI!""",
    ),
    (
        "Muhurta: Choosing Auspicious Times in India",
        "muhurta-auspicious-timing",
        "Muhurta is the Vedic science of choosing the most favorable time for important events. Essential for Indian weddings, business, and ceremonies.",
        "Muhurta",
        "Swami Anand Nath",
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&h=400&fit=crop",
        """# Muhurta: Choosing Auspicious Times in India

Muhurta (Muhurat) is the ancient Indian science of electing auspicious times. No major event in traditional Indian life—from weddings to business inaugurations—begins without consulting an astrologer for the right Muhurta.

## What is Muhurta?

Muhurta refers to a specific period of time (approximately 48 minutes) that is considered favorable for undertaking important activities. The selection is based on planetary positions, Tithi (lunar day), Nakshatra, and day of the week.

## Common Muhurtas in India

- **Vivah Muhurta** - Wedding ceremonies
- **Griha Pravesh** - Housewarming
- **Namkaran** - Baby naming ceremony
- **Business Inauguration** - Opening new ventures
- **Vehicle Purchase** - Buying car or property
- **Yagya and Puja** - Religious ceremonies

## Panchang: The Indian Almanac

Muhurta selection relies on the Panchang, the traditional Indian calendar that tracks Tithi, Vara, Nakshatra, Yoga, and Karana. Each day has specific auspicious and inauspicious periods.

## Inauspicious Periods to Avoid

- **Rahu Kaal** - 90 minutes daily (varies by weekday)
- **Gulika Kaal** - Another inauspicious period
- **Yamaganda** - Period of Yama (death)
- **Bhadra** - Inauspicious for travel
- **Eclipse periods** - Solar and lunar eclipses

Plan your important moments with AstroGuru AI's guidance!""",
    ),
    (
        "Vedic Astrology in Indian Weddings: A Complete Guide",
        "vedic-astrology-indian-weddings",
        "From Kundli Milan to Muhurta selection—how Vedic astrology shapes traditional Indian wedding ceremonies and matchmaking.",
        "Marriage",
        "AstroGuru Team",
        "https://images.unsplash.com/photo-1583939003579-730e3918a45a?w=800&h=400&fit=crop",
        """# Vedic Astrology in Indian Weddings: A Complete Guide

Vedic astrology is deeply woven into the fabric of Indian weddings. From the initial matchmaking to the final wedding Muhurta, astrological guidance shapes every step of the journey.

## Kundli Milan (Horoscope Matching)

In India, Kundli Milan involves matching 8 aspects (Ashtakoot) or 36 aspects (Dashakoot) of the bride and groom's birth charts. A minimum score is often required for the marriage to proceed.

## The Ashtakoot System

1. **Varna** - Spiritual compatibility
2. **Vashya** - Mutual attraction
3. **Tara** - Birth star compatibility
4. **Yoni** - Physical compatibility
5. **Graha Maitri** - Mental compatibility
6. **Gana** - Temperament (Deva, Manushya, Rakshasa)
7. **Bhakoot** - Emotional compatibility
8. **Nadi** - Health and progeny

## Gana Dosha

One of the most critical checks—Rakshasa Gana (Ashlesha, Magha, Jyeshtha) natives are incompatible with Deva/Manushya Gana. This is often a deal-breaker in arranged marriages.

## Wedding Muhurta

The wedding date and time are chosen based on:
- Auspicious Nakshatras (Rohini, Uttara Phalguni, etc.)
- Avoiding inauspicious periods
- Favorable planetary transits
- Family's birth charts

## Post-Wedding Rituals

Even Griha Pravesh (entering the new home) is timed according to Muhurta in traditional families.

Get your compatibility report with AstroGuru AI!""",
    ),
    (
        "Sade Sati: Saturn's Transit Through Your Moon Sign",
        "sade-sati-saturn-transit",
        "Sade Sati is the 7.5-year period when Saturn transits around your Moon sign. Understand its impact and remedies in Indian astrology.",
        "Transits",
        "Pt. Arun Bansal",
        "https://images.unsplash.com/photo-1465101162946-4377e57745c3?w=800&h=400&fit=crop",
        """# Sade Sati: Saturn's Transit Through Your Moon Sign

Sade Sati (Shani Sade Sati) is one of the most feared and discussed planetary periods in Indian Vedic astrology. When Saturn (Shani) transits through the 12th, 1st, and 2nd houses from your Moon sign, you experience this 7.5-year phase.

## The Three Phases

- **First Phase** - Saturn in 12th from Moon: Preparation, letting go
- **Second Phase** - Saturn in 1st from Moon: Peak intensity, transformation
- **Third Phase** - Saturn in 2nd from Moon: Stabilization, lessons learned

## Common Effects

- Career challenges and delays
- Health issues
- Financial strain
- Relationship difficulties
- Spiritual awakening (positive aspect)
- Karmic reckoning

## Remedies Practiced in India

- **Shani Shanti Puja** - Worship of Lord Shani
- **Donating to the poor** - Especially on Saturdays
- **Wearing Blue Sapphire** - Only after astrologer approval
- **Visiting Shani temples** - Shani Shingnapur, etc.
- **Chanting Shani Mantra** - "Om Shan Shanaischaraya Namah"
- **Lighting mustard oil lamp** - On Saturday evenings

## When Does Sade Sati Occur?

Sade Sati occurs roughly every 29.5 years in your life. Many Indians track their Sade Sati period and take preventive measures.

Check your Saturn transit with AstroGuru AI!""",
    ),
    (
        "Lagna: Your Rising Sign in Vedic Astrology",
        "lagna-rising-sign",
        "Lagna or Ascendant is the sign rising on the eastern horizon at birth. It's the most important point in your Vedic birth chart.",
        "Birth Chart",
        "Dr. Rajesh Sharma",
        "https://images.unsplash.com/photo-1532619675605-1ede6c2ed2b0?w=800&h=400&fit=crop",
        """# Lagna: Your Rising Sign in Vedic Astrology

In Vedic astrology, Lagna (Ascendant) is considered the most important point in your birth chart. It represents the sign that was rising on the eastern horizon at the exact moment of your birth and shapes your physical appearance, personality, and life approach.

## Why Lagna Matters

- **First House** - Lagna defines your 1st house, the house of self
- **Physical Appearance** - Your looks and demeanor
- **Life Direction** - How you approach life
- **Chart Ruler** - The Lagna lord influences your entire chart

## Lagna vs Rashi (Moon Sign)

- **Rashi** - Moon sign, your emotional nature (used for Dasha calculation)
- **Lagna** - Rising sign, your outer personality and life path
- Both are important; Indians often identify with both

## The Twelve Lagnas

Each of the 12 zodiac signs can be your Lagna, bringing unique characteristics. Aries Lagna natives are different from Cancer Lagna natives in fundamental ways.

## Lagna Lord (Lagnesh)

The planet ruling your Lagna sign becomes your Lagna lord. Its position and condition in your chart significantly influence your life's quality and direction.

## Importance in Indian Astrology

In India, the Lagna is used for timing events (Muhurta), predicting marriage (7th from Lagna), career (10th from Lagna), and more. It's the anchor of chart interpretation.

Discover your Lagna with AstroGuru AI!""",
    ),
    (
        "Divisional Charts (D-Charts) in Vedic Astrology",
        "divisional-charts-d-charts",
        "D-charts are harmonic charts that provide deeper insights. Learn about D9 (Navamsa), D10, D7 and their use in Indian astrology.",
        "Advanced",
        "Pt. Arun Bansal",
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&h=400&fit=crop",
        """# Divisional Charts (D-Charts) in Vedic Astrology

Divisional charts (Varga charts) are one of the unique strengths of Vedic astrology. By dividing each sign into smaller parts, we get more precise and detailed predictions—a technique refined over millennia in India.

## The Sixteen Vargas

Vedic astrology uses 16 divisional charts, each serving a specific purpose:
- **D1** - Rashi chart (main birth chart)
- **D9** - Navamsa (marriage, spirituality)
- **D10** - Dasamsa (career)
- **D7** - Saptamsa (children)
- **D4** - Chaturthamsa (property)
- And 11 more...

## Navamsa (D9) - The Most Important

Navamsa divides each sign into 9 parts. It's considered the "fruit" of the birth chart and is essential for:
- Marriage compatibility
- Spouse's nature
- Spiritual evolution
- Confirming Rashi chart predictions

## Dasamsa (D10) - Career Chart

The Dasamsa chart specifically reveals career, profession, and professional success. Many Indian astrologers use it for career guidance.

## How D-Charts Work

A planet strong in Rashi but weak in Navamsa may not deliver results. Strength in both charts indicates favorable outcomes. This dual-check system makes Vedic astrology remarkably accurate.

## Indian Astrology Tradition

The use of Vargas is documented in classical texts like BPHS (Brihat Parashara Hora Shastra). Indian astrologers routinely use at least D1 and D9 for important predictions.

Get a comprehensive chart analysis with AstroGuru AI!""",
    ),
    (
        "Indian Festivals and Their Astrological Significance",
        "indian-festivals-astrology",
        "Discover how Indian festivals like Diwali, Navratri, and Makar Sankranti are rooted in Vedic astrology and planetary movements.",
        "Festivals",
        "Swami Anand Nath",
        "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?w=800&h=400&fit=crop",
        """# Indian Festivals and Their Astrological Significance

Indian festivals are not arbitrary—they're precisely timed according to the lunar calendar (Panchang) and planetary positions. Each festival has deep astrological significance rooted in Vedic wisdom.

## Diwali - Festival of Lights

Diwali falls on Amavasya (new moon) of Kartik month. The darkest night symbolizes the victory of light over darkness. Lakhsmi Puja is performed during the most auspicious Muhurta of the year for wealth.

## Navratri - Nine Nights of the Goddess

Navratri occurs twice yearly during the transition of seasons (Vasanta and Sharad). The nine nights correspond to the nine forms of Durga and the nine planets (Navagrahas).

## Makar Sankranti - Sun's Transition

Makar Sankranti marks the Sun's entry into Capricorn (Makar). It's one of the few festivals based on the solar calendar. The Sun begins its northward journey (Uttarayan), considered highly auspicious.

## Holi - Full Moon of Phalgun

Holi is celebrated on the full moon (Purnima) of Phalgun month. The lunar-solar alignment creates a unique energetic shift celebrated with colors and joy.

## Other Astrological Festivals

- **Guru Purnima** - Full moon when Jupiter is strong
- **Shivaratri** - Darkest night, Shiva's night
- **Raksha Bandhan** - Full moon of Shravan
- **Janmashtami** - Krishna's birth, Rohini Nakshatra

## Muhurta for Festivals

Even within festival days, specific times (Muhurtas) are considered more auspicious for puja and rituals. Indians consult Panchang for these timings.

Celebrate with cosmic awareness!""",
    ),
    (
        "Vastu and Vedic Astrology: Harmonizing Your Space",
        "vastu-vedic-astrology",
        "Vastu Shastra and Vedic astrology work together to create harmonious living spaces. Learn how direction and planetary energies align.",
        "Remedies",
        "Rajiv Chopra",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=400&fit=crop",
        """# Vastu and Vedic Astrology: Harmonizing Your Space

Vastu Shastra (Indian architecture) and Vedic astrology are sister sciences. Both aim to align human life with cosmic energies. In India, new homes and offices are often designed with both Vastu and astrological considerations.

## The Connection

- **Directions and Planets** - Each direction is ruled by a planet (North-Kubera, South-Yama, East-Sun, etc.)
- **Birth Chart** - Your chart determines which directions favor you
- **Remedies** - Vastu corrections can mitigate planetary afflictions

## Eight Directions in Vastu

1. **East** - Sun, new beginnings, health
2. **West** - Saturn, stability
3. **North** - Mercury, wealth, prosperity
4. **South** - Mars, strength (main door often avoided)
5. **Northeast** - Jupiter, most auspicious (Ishan)
6. **Northwest** - Moon, travel
7. **Southeast** - Venus, fire, kitchen
8. **Southwest** - Rahu, master bedroom

## Vastu and Your Birth Chart

An astrologer can suggest:
- Best direction for your home's main entrance
- Ideal room placement based on your Lagna
- Colors and elements to balance your chart
- Placement of idols and sacred objects

## Common Vastu Remedies

- Mirrors to redirect energy
- Plants in specific corners
- Water elements in North
- Avoiding clutter in Northeast
- Proper placement of kitchen and bathroom

Align your space with cosmic harmony!""",
    ),
    (
        "Health and Ayurveda in Vedic Astrology",
        "health-ayurveda-vedic-astrology",
        "Explore the connection between Vedic astrology, Ayurveda, and health. How planetary positions influence your constitution and wellness.",
        "Health",
        "Dr. Rajesh Sharma",
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=400&fit=crop",
        """# Health and Ayurveda in Vedic Astrology

Vedic astrology and Ayurveda share the same philosophical roots. Both emerged from the Vedas and use similar frameworks—the five elements, three doshas, and planetary influences—to understand human health and constitution.

## Planets and Body Parts

- **Sun** - Heart, bones, vitality
- **Moon** - Mind, fluids, stomach
- **Mars** - Blood, muscles, marrow
- **Mercury** - Nervous system, skin
- **Jupiter** - Liver, fat, growth
- **Venus** - Reproductive system, throat
- **Saturn** - Joints, bones, chronic conditions
- **Rahu** - Skin, nervous disorders
- **Ketu** - Mysterious ailments, past life karma

## The Sixth and Eighth Houses

- **6th House** - Disease, daily health, enemies
- **8th House** - Chronic illness, longevity, transformation
- Afflictions to these houses indicate health challenges

## Ayurvedic Constitution (Prakriti)

Your birth chart can indicate your natural dosha balance (Vata, Pitta, Kapha). This helps in personalized Ayurvedic recommendations.

## Health Remedies in Indian Tradition

- **Gemstones** - To strengthen weak planets
- **Mantras** - For specific health issues
- **Herbs** - Planetary herbs (e.g., Saffron for Sun)
- **Fasting** - On planetary days
- **Charity** - To mitigate malefic effects

## Dasha and Health

Certain Dasha periods can trigger health issues. Knowing your Dasha timeline helps you take preventive measures and follow appropriate lifestyle practices.

Get personalized health insights with AstroGuru AI!""",
    ),
    (
        "Love and Compatibility: Vedic Astrology Perspective",
        "love-compatibility-vedic-astrology",
        "How does Vedic astrology view love and relationships? Explore the 7th house, Venus, and compatibility factors in Indian astrology.",
        "Relationships",
        "AstroGuru Team",
        "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?w=800&h=400&fit=crop",
        """# Love and Compatibility: Vedic Astrology Perspective

Vedic astrology offers a unique perspective on love and relationships, combining the 7th house (partnerships), Venus (love), and Mars (passion) with the traditional Kundli Milan system used in India.

## The 7th House - House of Partnership

The 7th house governs marriage, spouse, business partners, and all one-to-one relationships. Planets in or aspecting the 7th house shape your relationship destiny.

## Venus - Planet of Love

Venus (Shukra) represents love, beauty, romance, and marriage. A strong Venus indicates capacity for love and harmonious relationships. Venus in the 7th house often signifies a loving spouse.

## Mars - Planet of Passion

Mars adds passion and desire to relationships. Its placement affects physical compatibility and the dynamic of the partnership.

## Compatibility Beyond Kundli Milan

Beyond the traditional 36-point matching, modern Vedic astrologers also consider:
- Moon sign compatibility (emotional connection)
- Venus-Moon connection (romantic harmony)
- 5th house (romance) and 7th house (marriage) synergy
- Dasha compatibility (favorable timing)

## Remedies for Relationship Issues

- Strengthening Venus through gemstones or mantras
- Mangal Dosha remedies if applicable
- Worshipping Lord Krishna (divine love)
- Performing couples puja

## Love Marriage vs Arranged

Vedic astrology can analyze both scenarios—whether you're seeking a love marriage or going through arranged matchmaking, your chart reveals your relationship patterns and ideal partner qualities.

Find your compatibility with AstroGuru AI!""",
    ),
    (
        "Pitru Dosha: Ancestral Karma in Your Birth Chart",
        "pitru-dosha-ancestral-karma",
        "Pitru Dosha indicates ancestral karma affecting your chart. Learn about its effects and the Shradh and Tarpan remedies in Indian tradition.",
        "Remedies",
        "Swami Anand Nath",
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800&h=400&fit=crop",
        """# Pitru Dosha: Ancestral Karma in Your Birth Chart

Pitru Dosha (ancestral affliction) is a significant concept in Vedic astrology. It indicates that the soul has carried forward karmic debts or unfulfilled desires of ancestors, which can manifest as obstacles in life.

## What Causes Pitru Dosha?

- Sun, Moon, and Rahu in the 9th house (house of father, ancestors)
- Malefic planets in 9th house
- Rahu-Ketu axis affecting 9th house
- Inauspicious planetary combinations (Grahana Yoga, etc.)

## Effects of Pitru Dosha

- Delayed marriage or progeny
- Financial instability despite efforts
- Health issues, especially hereditary
- Obstacles in education and career
- Feeling of being "blocked" or unsupported
- Dreams of ancestors

## The Indian Tradition of Ancestor Worship

India has a rich tradition of honoring ancestors:
- **Shradh** - Annual rites for departed ancestors
- **Pitru Paksha** - 16-day period dedicated to ancestors (before Navratri)
- **Tarpan** - Offering water to ancestors
- **Pinda Daan** - Offering at Gaya and other sacred places

## Remedies for Pitru Dosha

- Performing Shradh with proper rituals
- Donating to the needy in ancestors' name
- Visiting pilgrimage sites (Gaya, Haridwar)
- Chanting Pitru Stotra
- Feeding crows (considered ancestors' messengers)
- Planting trees in ancestors' memory

## When to Perform Remedies

Pitru Paksha (the dark fortnight of Bhadrapada) is the most auspicious time for ancestor-related remedies. Many Indians perform elaborate Shradh during this period.

Heal ancestral patterns with AstroGuru AI's guidance!""",
    ),
    (
        "Graha Shanti: Pacifying Planetary Influences in India",
        "graha-shanti-planetary-remedies",
        "Graha Shanti are the traditional Indian rituals performed to pacify malefic planets. Learn about Navagraha Shanti and temple remedies.",
        "Remedies",
        "Pt. Arun Bansal",
        "https://images.unsplash.com/photo-1605639911300-0152a4c2476b?w=800&h=400&fit=crop",
        """# Graha Shanti: Pacifying Planetary Influences in India

Graha Shanti (planetary pacification) encompasses the various rituals, prayers, and remedies performed across India to mitigate the negative effects of malefic planets and strengthen favorable ones.

## Navagraha - The Nine Planets

In Hindu temples across India, you'll find the Navagraha shrine—nine idols representing Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu. Worshipping these deities is a common remedy.

## Types of Graha Shanti

- **Surya Shanti** - For Sun-related issues
- **Chandra Shanti** - For Moon-related issues
- **Mangal Shanti** - For Mars (Mangal Dosha, etc.)
- **Budh Shanti** - For Mercury
- **Guru Shanti** - For Jupiter
- **Shukra Shanti** - For Venus
- **Shani Shanti** - For Saturn (Sade Sati, etc.)
- **Rahu-Ketu Shanti** - For eclipse-related doshas

## Temple-Based Remedies

Famous planetary temples in India:
- **Surya** - Konark, Modhera, Arasavalli
- **Shani** - Shani Shingnapur, Shingnapur
- **Navagraha** - Navagraha temples in Tamil Nadu, Assam
- **Rahu-Ketu** - Kalahasti, various Naganathar temples

## Homas and Yagyas

Vedic fire rituals (Homas) are performed by priests to invoke planetary deities. These are often done during challenging Dasha periods or for specific life goals.

## Gemstones and Graha Shanti

Wearing gemstones is considered a form of Graha Shanti—bringing the planetary energy closer. However, wrong gemstones can worsen conditions; always consult an astrologer.

## Charity as Remedy

Donating items associated with each planet (e.g., wheat for Sun, white cloth for Moon) on their respective days is a simple yet powerful Graha Shanti practiced widely in India.

Balance your planets with AstroGuru AI!""",
    ),
    (
        "Famous Indian Astrologers and the Legacy of Jyotisha",
        "indian-astrologers-jyotisha-legacy",
        "From Varahamihira to modern practitioners—the rich tradition of Indian astrology and its masters who shaped Jyotisha over millennia.",
        "Basics",
        "AstroGuru Team",
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=400&fit=crop",
        """# Famous Indian Astrologers and the Legacy of Jyotisha

Jyotisha (Vedic astrology) has been practiced in India for over 5,000 years. This rich tradition has produced legendary astrologers whose works form the foundation of astrological practice even today.

## Ancient Masters

**Maharishi Parashara** (c. 3000 BCE) - Author of Brihat Parashara Hora Shastra (BPHS), the most comprehensive text on Vedic astrology. His systems of Dasha, Vargas, and chart interpretation are used worldwide.

**Maharishi Jaimini** - Developed the Jaimini system, an alternative approach using Karakas and Chara Dasha. His Upadesa Sutras are studied by advanced practitioners.

**Varahamihira** (505-587 CE) - Author of Brihat Jataka and Pancha Siddhantika. He synthesized Greek and Indian astronomical knowledge.

**Kalyana Varma** - Wrote Saravali, a classic text on planetary combinations and Yogas.

## Medieval and Modern Masters

**Mantreswara** - Phaladeepika, one of the most practical classical texts.

**Pandit Gopesh Kumar Ojha** - Modern pioneer who made classical texts accessible.

**Dr. B.V. Raman** - Brought Vedic astrology to the masses through his writings and the Astrological Magazine.

## The Living Tradition

Today, thousands of astrologers across India—from temple priests to PhD holders—continue this tradition. The government of India offers courses in Jyotisha at universities. The practice remains vibrant, evolving with technology while preserving ancient wisdom.

## AstroGuru AI: Ancient Wisdom, Modern Technology

AstroGuru AI combines this millennia-old tradition with cutting-edge AI, making personalized Vedic astrology insights accessible to everyone.

Start your journey with AstroGuru AI today!""",
    ),
]


def seed_articles():
    """Seed the database with sample articles. Uses ON CONFLICT to skip existing slugs (idempotent)."""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        print("Connected to database successfully")

        insert_query = """
        INSERT INTO articles (title, slug, excerpt, category, author, featured_image, content, is_published, view_count, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO NOTHING
        """

        now = datetime.utcnow()
        inserted = 0
        for title, slug, excerpt, category, author, image, content in SAMPLE_ARTICLES:
            cursor.execute(
                insert_query,
                (title, slug, excerpt, category, author, image, content, True, 0, now, now),
            )
            inserted += cursor.rowcount

        conn.commit()

        print(f"Seeded {inserted} new articles ({len(SAMPLE_ARTICLES) - inserted} already existed)")
        print(f"Total articles in database: {len(SAMPLE_ARTICLES)}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error seeding articles: {e}")
        raise


if __name__ == "__main__":
    seed_articles()
