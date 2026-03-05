import { motion } from 'framer-motion';

const AboutSection = () => {
  const coreFeatures = [
    {
      icon: '🧠',
      title: 'Vedic Expertise',
      description: '5000+ years of proven Vedic astrology wisdom',
    },
    {
      icon: '⚡',
      title: 'AI-Powered Analysis',
      description: 'Lightning-fast AI-driven analysis and insights',
    },
    {
      icon: '💫',
      title: 'Personalized',
      description: 'Customized readings tailored to your unique chart',
    },
  ];

  const services = [
    {
      icon: '📊',
      title: 'Birth Chart Analysis',
      description: 'Complete Janam Kundli interpretation',
    },
    {
      icon: '🎯',
      title: 'Career Guidance',
      description: 'Unlock your professional potential',
    },
    {
      icon: '✨',
      title: 'Relationship Insights',
      description: 'Love and compatibility analysis',
    },
    {
      icon: '💚',
      title: 'Health Predictions',
      description: 'Wellness and healing guidance',
    },
  ];



  return (
    <section className="py-24 md:py-32 relative overflow-hidden bg-slate-50 dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        {/* Main Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-slate-900 dark:text-white">
            About AstroGuru
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Combining 5000 years of Vedic astrology wisdom with advanced AI to provide personalized cosmic insights that guide your life decisions.
          </p>
        </motion.div>

        {/* Core Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-24">
          {coreFeatures.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="card p-8 border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all duration-300"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">{feature.title}</h3>
              <p className="text-slate-600 dark:text-slate-400">{feature.description}</p>
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
          <h3 className="text-3xl font-bold text-center mb-12 text-slate-900 dark:text-white">Our Services</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {services.map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="flex gap-4 p-6 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:shadow-md transition-all"
              >
                <div className="flex-shrink-0 text-3xl">{service.icon}</div>
                <div>
                  <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">{service.title}</h4>
                  <p className="text-slate-600 dark:text-slate-400 text-sm">{service.description}</p>
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
          className="rounded-xl bg-indigo-50 dark:bg-slate-800 border border-indigo-200 dark:border-slate-700 p-12"
        >
          <h3 className="text-3xl font-bold text-center mb-12 text-slate-900 dark:text-white">Why Choose AstroGuru</h3>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { title: 'Accurate', desc: 'AI-powered predictions' },
              { title: 'Expert', desc: 'Seasoned astrologers' },
              { title: 'Fast', desc: 'Instant analysis' },
              { title: 'Private', desc: 'Enterprise security' },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">{item.title}</h4>
                <p className="text-slate-600 dark:text-slate-400 text-sm">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-20 pt-20 border-t border-slate-200 dark:border-slate-700"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              whileHover={{ y: -4 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">10K+</div>
              <p className="text-slate-600 dark:text-slate-400">Happy Users</p>
            </motion.div>
            <motion.div
              whileHover={{ y: -4 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">98%</div>
              <p className="text-slate-600 dark:text-slate-400">Satisfaction</p>
            </motion.div>
            <motion.div
              whileHover={{ y: -4 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">5K+</div>
              <p className="text-slate-600 dark:text-slate-400">Predictions</p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default AboutSection;
