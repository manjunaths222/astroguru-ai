"""Seed script to populate articles table with sample Vedic Astrology content"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database, SessionLocal, Base, engine
from models.article import Article

# Sample articles about Vedic Astrology
SAMPLE_ARTICLES = [
    {
        "title": "Introduction to Vedic Astrology: Ancient Wisdom for Modern Times",
        "slug": "introduction-vedic-astrology",
        "excerpt": "Discover the foundations of Vedic Astrology, one of the oldest and most accurate systems of astrology known to humanity.",
        "category": "Basics",
        "author": "AstroGuru Team",
        "content": """
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

Start your journey with AstroGuru AI today and discover your cosmic destiny!
""",
        "featured_image": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=500&h=300&fit=crop"
    },
    {
        "title": "Understanding Your Birth Chart (Janam Kundli)",
        "slug": "understanding-birth-chart",
        "excerpt": "Learn how to read and interpret your natal chart - the cosmic snapshot at the moment of your birth.",
        "category": "Basics",
        "author": "AstroGuru Team",
        "content": """
Your Birth Chart, or Janam Kundli, is the cosmic blueprint of your life. It's a map of the exact positions of the planets at the moment of your birth, serving as a guide to your destiny, strengths, challenges, and opportunities.

## The Components of Your Birth Chart

### 1. The Twelve Houses (Bhavas)
Each house represents a different area of your life:
- **House 1** - Self, appearance, personality
- **House 2** - Wealth, family, speech
- **House 3** - Courage, siblings, communication
- **House 4** - Home, mother, property, peace
- **House 5** - Children, creativity, romance
- **House 6** - Health, enemies, debts
- **House 7** - Marriage, partnerships, public image
- **House 8** - Longevity, transformation, occult
- **House 9** - Fortune, higher education, spirituality
- **House 10** - Career, reputation, public life
- **House 11** - Gains, friends, achievements
- **House 12** - Losses, separation, liberation

### 2. The Ascendant (Lagna)
The Ascendant is the zodiac sign on the eastern horizon at the exact moment and place of your birth. It represents your physical appearance, personality, and how you present yourself to the world.

### 3. Planetary Positions
The positions of the nine planets in various houses and signs reveal your talents, strengths, and challenges.

### 4. Aspects (Drishti)
Aspects are the angular relationships between planets. They indicate how different areas of your life are influenced by planetary energies.

## How to Interpret Your Birth Chart

To interpret your birth chart, you need:
- Your exact birth time
- Your birth date
- Your birth location

With this information, an astrologer can create an accurate Janam Kundli and provide detailed insights into your life journey.

## Get Your Free Birth Chart Analysis

Visit AstroGuru AI today to get your personalized birth chart analysis and unlock the secrets of your cosmic blueprint!
""",
        "featured_image": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=500&h=300&fit=crop"
    },
    {
        "title": "The Power of Planetary Transits and Their Impact on Your Life",
        "slug": "planetary-transits-impact",
        "excerpt": "Understand how current planetary movements influence your daily life and future prospects.",
        "category": "Advanced",
        "author": "AstroGuru Team",
        "content": """
Planetary Transits are the movements of planets through the zodiac, creating various astrological events throughout your life. These transits have a direct impact on your experiences, decisions, and destiny.

## What are Transits?

Transits occur when a planet moves into a specific house or forms an aspect with a planet in your natal chart. Each transit has a different duration and significance. Some transits last a few days, while others last years.

## Major Planetary Transits

### Saturn Transit (Sade Sati)
The Saturn Return or Sade Sati is a significant 7.5-year period when Saturn transits through the zodiac sign where the Moon was at your birth. This period is often challenging but transformative, bringing maturity and wisdom.

### Jupiter Transit
Jupiter's transit brings expansion, prosperity, and opportunities. A beneficial Jupiter transit can open doors to success in various areas of life.

### Mars Transit
Mars transits bring energy, courage, and sometimes aggression. During favorable Mars transits, you may feel motivated to take action on your goals.

### Rahu and Ketu Transits
Rahu and Ketu transits (18.6-year cycles) bring significant life changes and spiritual growth. These are important periods for transformation.

## How Transits Affect You

Transits create opportunities and challenges based on:
- Your natal chart
- The planet in transit
- The house or planet being transited
- The aspect formed

## Making the Most of Planetary Transits

Understanding your planetary transits helps you:
- Plan important life decisions
- Prepare for challenges
- Seize opportunities
- Navigate life transitions smoothly

Get personalized transit reports from AstroGuru AI and navigate your future with confidence!
""",
        "featured_image": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=500&h=300&fit=crop"
    },
    {
        "title": "Career Success Through Vedic Astrology: Finding Your Dharma",
        "slug": "career-success-vedic-astrology",
        "excerpt": "Discover your ideal career path and professional strengths using your birth chart analysis.",
        "category": "Career",
        "author": "AstroGuru Team",
        "content": """
Your career is one of the most important aspects of your life. Vedic Astrology can help you understand your natural talents, ideal career paths, and the best times to make career moves.

## Career Houses in Your Birth Chart

### House 10 (Karma)
The 10th house represents your career, reputation, and public image. Strong planets in this house indicate success in your professional life.

### House 2 (Wealth)
The 2nd house represents your earning potential and financial stability. Good placements here suggest prosperity.

### House 5 (Creativity)
The 5th house represents creative pursuits and intellectual work. This house is important for those in creative fields.

## Planetary Indicators of Career Success

- **Sun in strong position** - Leadership qualities, public recognition
- **Mercury prominent** - Communication, business, trading
- **Jupiter well-placed** - Teaching, law, spirituality, expansion
- **Saturn strong** - Discipline, engineering, scientific work
- **Mars in 10th** - Entrepreneurship, military, sports

## Yogas for Career Success

Certain planetary combinations (Yogas) create exceptional career opportunities:
- **Rajayoga** - Royal combinations bringing power and success
- **Dhanyoga** - Wealth-creating combinations
- **Vidyayoga** - Combinations for knowledge and education

## Finding Your Dharma (Life Purpose)

Your birth chart reveals your Dharma - your unique life purpose and calling. By understanding this, you can align your career with your soul's mission.

## Timing Your Career Moves

Vedic Astrology helps identify auspicious times for:
- Job changes or promotions
- Starting a business
- Major career decisions
- Professional transformations

Unlock your full career potential with personalized guidance from AstroGuru AI!
""",
        "featured_image": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=500&h=300&fit=crop"
    },
    {
        "title": "Love, Marriage & Relationships: The Venus Factor in Your Chart",
        "slug": "love-marriage-relationships",
        "excerpt": "Explore how Venus and other planets influence your romantic destiny and relationship potential.",
        "category": "Relationships",
        "author": "AstroGuru Team",
        "content": """
Love and relationships are fundamental to human happiness. Vedic Astrology provides deep insights into your romantic nature, compatibility, and the timing of important relationship events.

## Venus: The Planet of Love

Venus is the planet governing love, beauty, and relationships. Its position in your birth chart reveals:
- Your romantic nature
- What you're attracted to
- How you express love and affection
- Your relationship potential

## Houses of Relationships

### House 7 (Marriage)
The 7th house is the primary indicator of marriage and partnerships. Strong planets here indicate successful relationships.

### House 5 (Romance)
The 5th house represents romance, dating, and love affairs. This house is important for understanding your romantic inclinations.

### House 8 (Intimacy)
The 8th house represents intimate connections and transformation through relationships.

## Relationship Compatibility (Synastry)

Vedic Astrology uses Synastry - the comparison of two birth charts - to assess compatibility:
- **Guna Milan** - Matching of 36 qualities
- **Planetary Aspects** - How planets in each chart affect the other
- **Vimshottari Dasha** - Favorable time periods for relationships

## Marriage Timing

Vedic Astrology helps identify:
- Auspicious times for marriage
- Potential marriage ages
- Planetary periods (Dashas) favorable for marriage
- Remedies for marriage delays

## Common Relationship Challenges

Certain planetary combinations can create relationship challenges:
- **Saturn aspects to Venus** - Delays or distance in relationships
- **Rahu/Ketu affecting 7th house** - Unconventional relationships
- **Mars aspects** - Arguments and conflicts

## Remedies for Relationship Harmony

Vedic Astrology offers remedies including:
- Gemstone recommendations
- Mantra chanting
- Ritual observances
- Compatibility enhancements

Discover your romantic destiny and find harmony in relationships with AstroGuru AI!
""",
        "featured_image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=500&h=300&fit=crop"
    },
    {
        "title": "Health & Wellness: Astrology's Approach to Well-being",
        "slug": "health-wellness-astrology",
        "excerpt": "Learn how planetary positions influence your physical health and overall wellness journey.",
        "category": "Health",
        "author": "AstroGuru Team",
        "content": """
Health is wealth, and Vedic Astrology offers unique insights into your physical and mental well-being. Your birth chart can reveal health tendencies and suggest preventive measures.

## Health Houses in Astrology

### House 1 (Ascendant)
The 1st house represents your overall health and vitality.

### House 6 (Health & Illness)
The 6th house specifically governs health, diseases, and recovery. Weak planets here may indicate health challenges.

### House 8 (Longevity)
The 8th house represents lifespan and chronic conditions.

## Planetary Influences on Health

- **Sun** - Heart, vital energy, immunity
- **Moon** - Mental health, emotional balance, immune system
- **Mars** - Inflammation, accidents, surgery
- **Mercury** - Nervous system, digestion, communication-related stress
- **Jupiter** - Overall wellness, liver health
- **Venus** - Reproductive health, skin conditions
- **Saturn** - Chronic conditions, spine, skeletal system
- **Rahu** - Confusion, infections, unusual diseases
- **Ketu** - Weaknesses, hidden health issues

## Health Analysis Through Your Chart

A comprehensive health analysis considers:
- Planetary positions in health houses
- Aspects to health-indicating planets
- Dashas (planetary periods) affecting health
- Remedial measures

## Preventive Health Measures

Vedic Astrology recommends:
- Gemstones to strengthen weak planets
- Dietary recommendations based on your constitution
- Yoga and meditation practices
- Auspicious timing for surgeries and treatments
- Herbal remedies aligned with your chart

## Mental Health & Emotional Balance

Your Moon sign and mental strength indicators reveal:
- Emotional tendencies
- Stress triggers
- Peace-bringing activities
- Meditation practices suitable for you

## Wellness During Challenging Periods

During difficult planetary periods (Dashas), specific wellness practices can maintain balance:
- Strengthening foods
- Spiritual practices
- Medical check-ups
- Lifestyle adjustments

Achieve holistic health and wellness with personalized guidance from AstroGuru AI!
""",
        "featured_image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=500&h=300&fit=crop"
    }
]


def seed_articles():
    """Populate the articles table with sample data"""
    
    # Initialize database
    init_database()
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if articles already exist
        existing_count = db.query(Article).count()
        
        if existing_count > 0:
            print(f"✓ Database already contains {existing_count} articles. Skipping seed...")
            return
        
        print("🌱 Seeding Vedic Astrology articles...")
        
        # Create article objects
        articles = []
        for article_data in SAMPLE_ARTICLES:
            article = Article(
                title=article_data["title"],
                slug=article_data["slug"],
                excerpt=article_data["excerpt"],
                content=article_data["content"],
                category=article_data["category"],
                author=article_data["author"],
                featured_image=article_data.get("featured_image"),
                is_published=True,
                view_count=0
            )
            articles.append(article)
        
        # Add all articles to database
        db.add_all(articles)
        db.commit()
        
        print(f"✓ Successfully seeded {len(articles)} articles!")
        print("  Articles added:")
        for article in articles:
            print(f"    - {article.title}")
            
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding articles: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_articles()
