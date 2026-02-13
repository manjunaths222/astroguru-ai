"""Constants for AstroGuru AI - Gochara (Planetary Transits) Data"""

# Gochara (Planetary Transit) Data
# These transits are used to provide context for predictions in goal analysis, recommendations, and summaries

GOCHARA_JUPITER = """
Jupiter Gochara (Transits):
- Gemini: Till June 2, 2026
- Cancer: From June 2, 2026 to October 31, 2026
- Leo: From October 31, 2026 to January 25, 2027
- Cancer: From January 25, 2027 to June 26, 2027
- Leo: From June 26, 2027 to November 26, 2027
- Virgo: From November 26, 2027 to February 28, 2028
- Leo: From February 28, 2028 to July 24, 2028
- Virgo: From July 24, 2028 to December 26, 2028
- Libra: From December 26, 2028 to March 29, 2029
- Virgo: From March 29, 2029 to August 25, 2029
- Libra: From August 25, 2029 to January 25, 2030
- Scorpio: From January 25, 2030 to May 1, 2030
- Libra: From May 1, 2030 to September 23, 2030
- Scorpio: From September 23, 2030 to February 17, 2031
- Sagittarius: From February 17, 2031 to June 14, 2031
- Scorpio: From June 14, 2031 to October 15, 2031
- Sagittarius: From October 15, 2031 to March 5, 2032
"""

GOCHARA_SATURN = """
Saturn Gochara (Transits):
- Pisces: Till June 3, 2027
- Aries: From June 3, 2027 to October 20, 2027
- Pisces: From October 20, 2027 to February 23, 2028
- Aries: From February 23, 2028 to August 8, 2029
- Taurus: From August 8, 2029 to October 5, 2029
- Aries: From October 5, 2029 to April 17, 2030
- Taurus: From April 17, 2030 to May 31, 2032
"""

GOCHARA_RAHU = """
Rahu Gochara (Transits):
- Aquarius: Till December 5, 2026
- Capricorn: From December 5, 2026 to June 23, 2028
- Sagittarius: From June 23, 2028 to January 11, 2030
- Scorpio: From January 11, 2030 to July 31, 2031
- Libra: From July 31, 2031 to February 16, 2033
"""

GOCHARA_KETU = """
Ketu Gochara (Transits):
- Leo: Till December 5, 2026
- Cancer: From December 5, 2026 to June 23, 2028
- Gemini: From June 23, 2028 to January 11, 2030
- Taurus: From January 11, 2030 to July 31, 2031
- Aries: From July 31, 2031 to February 16, 2033
"""

# Combined gochara context for use in nodes
GOCHARA_CONTEXT = f"""
**IMPORTANT: Gochara (Planetary Transit) Context for Predictions**

When making predictions and recommendations, you MUST consider the following planetary transits (Gochara) along with the Dasha periods:

{GOCHARA_JUPITER}

{GOCHARA_SATURN}

{GOCHARA_RAHU}

{GOCHARA_KETU}

When providing dates and time periods in your analysis, reference the specific Gochara transit periods above to make accurate predictions.
"""

