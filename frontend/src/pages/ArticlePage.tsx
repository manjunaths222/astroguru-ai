import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from '@/components/layout/Navbar';
import api from '@/utils/api';

interface Article {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  category: string;
  author: string;
  featured_image?: string;
  view_count: number;
  created_at: string;
  updated_at: string;
}

const ArticlePage = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchArticle();
  }, [slug]);

  const fetchArticle = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/api/v1/articles/${slug}`);
      setArticle(response.data);
    } catch (err) {
      console.error('Error fetching article:', err);
      setError('Article not found');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const parseMarkdown = (content: string) => {
    // Simple markdown parser for basic formatting
    let html = content
      .replace(/^### (.*?)$/gm, '<h3 class="text-2xl font-bold text-text-primary mt-6 mb-3">$1</h3>')
      .replace(/^## (.*?)$/gm, '<h2 class="text-3xl font-bold text-text-primary mt-8 mb-4">$1</h2>')
      .replace(/^# (.*?)$/gm, '<h1 class="text-4xl font-bold text-text-primary mt-10 mb-5">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-text-primary">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/^- (.*?)$/gm, '<li class="ml-6 mb-2">$1</li>')
      .replace(/(<li.*?<\/li>)/s, '<ul class="list-disc ml-4 mb-4">$1</ul>')
      .replace(/\n\n+/g, '</p><p class="mb-4 leading-relaxed">')
      .replace(/^(?!<[^>]*>)(.*?)$/gm, '<p class="mb-4 leading-relaxed">$1</p>');

    // Clean up empty paragraphs
    html = html.replace(/<p class="mb-4 leading-relaxed"><\/p>/g, '');
    html = html.replace(/<\/p><p class="mb-4 leading-relaxed">/g, '</p><p class="mb-4 leading-relaxed">');

    return html;
  };

  if (loading) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-20">
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="card h-96 bg-gradient-to-br from-slate-700 to-slate-800 animate-pulse"
          />
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-4xl font-bold text-text-primary mb-4">Article Not Found</h1>
            <p className="text-text-secondary mb-8">{error}</p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              className="btn-primary"
            >
              Back to Home
            </motion.button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <Navbar />

      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-10"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      <div className="max-w-4xl mx-auto px-4 py-12 relative z-10">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-primary hover:text-secondary transition-colors mb-8"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Articles
        </motion.button>

        <motion.article
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Featured Image */}
          {article.featured_image && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              className="mb-8 rounded-2xl overflow-hidden h-96 bg-gradient-to-br from-slate-700 to-slate-900"
            >
              <img
                src={article.featured_image}
                alt={article.title}
                className="w-full h-full object-cover"
              />
            </motion.div>
          )}

          {/* Header */}
          <div className="mb-8">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-3 mb-4"
            >
              <span className="px-4 py-1 rounded-full text-sm font-semibold text-white bg-gradient-to-r from-primary to-secondary">
                {article.category}
              </span>
              <span className="text-text-secondary text-sm">{formatDate(article.created_at)}</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="text-5xl font-bold text-text-primary mb-4"
            >
              {article.title}
            </motion.h1>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex items-center gap-4 text-text-secondary border-b border-white/10 pb-4"
            >
              <div>
                <p className="font-semibold text-text-primary">{article.author}</p>
                <p className="text-sm">Posted on {formatDate(article.created_at)}</p>
              </div>
              <div className="ml-auto flex items-center gap-2 text-primary">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <span>{article.view_count} views</span>
              </div>
            </motion.div>
          </div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.35 }}
            className="prose prose-invert max-w-none text-text-primary"
          >
            <div
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: parseMarkdown(article.content) }}
            />
          </motion.div>
        </motion.article>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-16 card bg-gradient-to-r from-primary/20 to-secondary/20 border border-primary/30 text-center"
        >
          <h3 className="text-2xl font-bold text-text-primary mb-4">
            Ready to Discover Your Cosmic Destiny?
          </h3>
          <p className="text-text-secondary mb-6 max-w-xl mx-auto">
            Get your personalized Vedic astrology analysis and start your journey towards clarity, success, and fulfillment.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary"
          >
            Get Your Analysis
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
};

export default ArticlePage;
