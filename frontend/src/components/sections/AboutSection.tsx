import { motion } from 'framer-motion';
import { Star, Zap, Heart, Brain, Target, Sparkles } from 'lucide-react';

const AboutSection = () => {
  const coreFeatures = [
    {
      icon: <Brain className="w-8 h-8" />,
      title: 'Vedic Expertise',
      description: '5000+ years of proven Vedic astrology wisdom',
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'AI-Powered Analysis',
      description: 'Lightning-fast AI-driven analysis and insights',
    },
    {
      icon: <Heart className="w-8 h-8" />,
      title: 'Personalized',
      description: 'Customized readings tailored to your unique chart',
    },
  ];

  const services = [
    {
      icon: <Star className="w-6 h-6" />,
      title: 'Birth Chart Analysis',
      description: 'Complete Janam Kundli interpretation',
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: 'Career Guidance',
      description: 'Unlock your professional potential',
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'Relationship Insights',
      description: 'Love and compatibility analysis',
    },
    {
      icon: <Heart className="w-6 h-6" />,
      title: 'Health Predictions',
      description: 'Wellness and healing guidance',
    },
  ];

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



  return (
    <section className="py-20 relative overflow-hidden bg-gradient-to-b from-background/50 via-background to-background/50">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-20 -right-20 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl opacity-10"
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
        <motion.div
          className="absolute -bottom-20 -left-20 w-96 h-96 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{
            scale: [1.1, 1, 1.1],
            y: [0, -30, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 relative z-10">
        {/* Main Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <motion.div
            className="inline-block mb-4"
            animate={{ rotate: [0, 5, 0, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            <span className="text-5xl">✨</span>
          </motion.div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 text-text-primary leading-tight">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-indigo-400 to-secondary">AstroGuru</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Bridging ancient Vedic wisdom with modern AI technology to unlock your cosmic destiny and guide your life's journey
          </p>
        </motion.div>

        {/* Core Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-24">
          {coreFeatures.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              viewport={{ once: true }}
              whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(99, 102, 241, 0.15)' }}
              className="card p-8 hover:shadow-2xl transition-all duration-300 border border-primary/10 hover:border-primary/30"
            >
              <motion.div
                className="flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 mb-6 text-primary"
                whileHover={{ scale: 1.1, rotate: 10 }}
              >
                {feature.icon}
              </motion.div>
              <h3 className="text-2xl font-bold mb-3 text-text-primary">{feature.title}</h3>
              <p className="text-text-secondary text-lg">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Services Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-24"
        >
          <h3 className="text-4xl font-bold text-center mb-12 text-text-primary">Our Services</h3>
          <div className="grid md:grid-cols-2 gap-8">
            {services.map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ x: 8 }}
                className="flex gap-6 p-6 rounded-lg bg-background/50 border border-primary/10 hover:border-primary/30 transition-all"
              >
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-gradient-to-br from-primary/30 to-secondary/30 text-primary">
                    {service.icon}
                  </div>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-text-primary mb-2">{service.title}</h4>
                  <p className="text-text-secondary">{service.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Why Choose Us Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="rounded-2xl bg-gradient-to-r from-primary/10 via-secondary/5 to-primary/10 border border-primary/20 p-12"
        >
          <h3 className="text-3xl font-bold text-center mb-12 text-text-primary">Why AstroGuru Stands Out</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { title: 'Accurate AI', desc: 'ML-powered predictions' },
              { title: 'Expert Team', desc: 'Seasoned astrologers' },
              { title: 'Instant Results', desc: 'Minutes, not days' },
              { title: 'Complete Privacy', desc: 'Enterprise encryption' },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <h4 className="text-lg font-semibold text-text-primary mb-2">{item.title}</h4>
                <p className="text-text-secondary">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-20"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center p-8 rounded-lg bg-background/50 border border-primary/10"
            >
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary mb-2">10,000+</div>
              <p className="text-text-secondary text-lg">Happy Users</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center p-8 rounded-lg bg-background/50 border border-primary/10"
            >
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary mb-2">98%</div>
              <p className="text-text-secondary text-lg">Satisfaction Rate</p>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-center p-8 rounded-lg bg-background/50 border border-primary/10"
            >
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary mb-2">5000+</div>
              <p className="text-text-secondary text-lg">Accurate Predictions</p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default AboutSection;
