"""Seed script to populate articles table with sample Vedic Astrology content"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Get database URL from environment
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:your_password@localhost:5432/astroguru"
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
]


def seed_articles():
    """Seed the database with sample articles"""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("[v0] Connected to database successfully")
        
        # Create articles table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            excerpt TEXT NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100),
            author VARCHAR(255),
            featured_image VARCHAR(500),
            is_published BOOLEAN DEFAULT TRUE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("[v0] Articles table created/exists")
        
        # Check if articles already exist
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"[v0] {count} articles already exist. Skipping seed.")
            cursor.close()
            conn.close()
            return
        
        # Insert sample articles
        insert_query = """
        INSERT INTO articles (title, slug, excerpt, category, author, featured_image, content, is_published, view_count, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        now = datetime.utcnow()
        values = [(title, slug, excerpt, category, author, image, content, True, 0, now, now) 
                  for title, slug, excerpt, category, author, image, content in SAMPLE_ARTICLES]
        
        cursor.executemany(insert_query, values)
        conn.commit()
        
        print(f"[v0] Successfully seeded {len(SAMPLE_ARTICLES)} articles into the database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[v0] Error seeding articles: {e}")
        raise


if __name__ == "__main__":
    seed_articles()
