import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import ArticleCard from './ArticleCard';
import api from '@/utils/api';

interface Article {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  category: string;
  author: string;
  featured_image?: string;
  view_count: number;
  created_at: string;
}

interface ArticlesSectionProps {
  title?: string;
  limit?: number;
  showCategories?: boolean;
  showViewAllLink?: boolean;
}

const ArticlesSection = ({
  title = 'Vedic Astrology Blog',
  limit = 6,
  showCategories = true,
  showViewAllLink = false,
}: ArticlesSectionProps) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: '0',
      });

      if (selectedCategory) {
        params.append('category', selectedCategory);
      }

      const response = await api.get(`/api/v1/articles?${params}`);
      setArticles(response.data);
    } catch (err) {
      console.error('Error fetching articles:', err);
      setError('Failed to load articles');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, limit]);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/articles/categories');
      setCategories(response.data.categories || []);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  }, []);

  useEffect(() => {
    fetchArticles();
    if (showCategories) {
      fetchCategories();
    }
  }, [fetchArticles, fetchCategories, showCategories]);

  return (
    <section className="py-20 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-secondary rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute bottom-0 left-1/4 w-80 h-80 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{
            scale: [1.2, 1, 1.2],
            x: [0, -50, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <motion.h2 className="text-4xl md:text-5xl font-bold text-text-primary mb-4">
            {title}
          </motion.h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto">
            Explore insightful articles and guides about Vedic Astrology, learn about your cosmic destiny, and discover how the stars influence your life.
          </p>
        </motion.div>

        {/* Category Filter */}
        {showCategories && categories.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex flex-wrap justify-center gap-3 mb-12"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedCategory(null)}
              className={`px-4 py-2 rounded-full font-semibold transition-all ${
                selectedCategory === null
                  ? 'bg-primary text-white shadow-lg'
                  : 'bg-surface text-text-primary hover:bg-primary/20'
              }`}
            >
              All Articles
            </motion.button>
            {categories.map((cat) => (
              <motion.button
                key={cat}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-full font-semibold transition-all ${
                  selectedCategory === cat
                    ? 'bg-primary text-white shadow-lg'
                    : 'bg-surface text-text-primary hover:bg-primary/20'
                }`}
              >
                {cat}
              </motion.button>
            ))}
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="card h-96 bg-gradient-to-br from-slate-700 to-slate-800 animate-pulse"
              />
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="text-red-400 text-lg">{error}</p>
          </motion.div>
        )}

        {/* Articles Grid */}
        {!loading && articles.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {articles.map((article, index) => (
              <ArticleCard key={article.id} {...article} index={index} />
            ))}
          </motion.div>
        )}

        {/* View All Articles - at the end */}
        {showViewAllLink && !loading && articles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="mt-16 text-center"
          >
            <Link
              to="/articles"
              className="inline-block px-8 py-3 rounded-lg font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
            >
              View All Articles
            </Link>
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && articles.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="text-text-secondary text-lg">
              {selectedCategory
                ? `No articles found in ${selectedCategory} category`
                : 'No articles available'}
            </p>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default ArticlesSection;
