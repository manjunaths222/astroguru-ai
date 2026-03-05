import { motion } from 'framer-motion';

const AboutSection = () => {
  const features = [
    {
      icon: '✨',
      title: 'AI-Powered Analysis',
      description: 'Advanced AI combines Vedic astrology with modern technology for accurate insights',
    },
    {
      icon: '🔮',
      title: 'Comprehensive Reports',
      description: 'Detailed birth chart analysis, planetary transits, and life predictions',
    },
    {
      icon: '💬',
      title: 'Expert Guidance',
      description: 'Interactive chat support to answer your specific astrology questions',
    },
    {
      icon: '📊',
      title: 'Personalized Insights',
      description: 'Custom recommendations based on your unique birth chart and cosmic energy',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <section className="py-20 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-20 -left-20 w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{
            scale: [1, 1.1, 1],
            y: [0, 30, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 relative z-10">
        {/* Main About Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mb-20"
        >
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              <motion.h2
                variants={itemVariants}
                className="text-4xl md:text-5xl font-bold text-text-primary mb-6"
              >
                Welcome to <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">AstroGuru AI</span>
              </motion.h2>

              <motion.p
                variants={itemVariants}
                className="text-text-secondary text-lg mb-4 leading-relaxed"
              >
                Discover the ancient wisdom of Vedic Astrology enhanced with cutting-edge artificial intelligence. AstroGuru AI brings you personalized astrological insights that guide your life decisions, reveal your cosmic purpose, and illuminate your path to success and happiness.
              </motion.p>

              <motion.p
                variants={itemVariants}
                className="text-text-secondary text-lg mb-6 leading-relaxed"
              >
                Whether you're seeking clarity on career choices, relationship compatibility, health concerns, or spiritual growth, our AI-powered analysis of your birth chart provides comprehensive guidance grounded in thousands of years of Vedic traditions.
              </motion.p>

              <motion.div
                variants={itemVariants}
                className="flex flex-wrap gap-4"
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-primary"
                >
                  Get Started
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-secondary"
                >
                  Learn More
                </motion.button>
              </motion.div>
            </motion.div>

            {/* Right Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative h-96 hidden md:block"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-primary/30 to-secondary/30 rounded-3xl blur-2xl"
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0],
                }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
              <div className="absolute inset-0 card flex items-center justify-center text-6xl">
                🔮
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-4xl font-bold text-text-primary text-center mb-16"
          >
            Our Services & Features
          </motion.h3>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -10, shadow: '0 20px 40px rgba(0,0,0,0.3)' }}
                className="card"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 + 0.3 }}
                  className="text-5xl mb-4"
                >
                  {feature.icon}
                </motion.div>
                <h4 className="text-xl font-bold text-text-primary mb-3">{feature.title}</h4>
                <p className="text-text-secondary leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Why Choose Us */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-20 card bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/30"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl font-bold text-primary mb-2">10,000+</div>
              <p className="text-text-secondary">Happy Users</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl font-bold text-primary mb-2">98%</div>
              <p className="text-text-secondary">Satisfaction Rate</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center"
            >
              <div className="text-4xl font-bold text-primary mb-2">5000+</div>
              <p className="text-text-secondary">Accurate Predictions</p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default AboutSection;
