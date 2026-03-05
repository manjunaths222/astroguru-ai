import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useState } from 'react';

interface ArticleCardProps {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  category: string;
  author: string;
  featured_image?: string;
  view_count: number;
  created_at: string;
  index?: number;
}

const ArticleCard = ({
  title,
  slug,
  excerpt,
  category,
  author,
  featured_image,
  view_count,
  created_at,
  index = 0,
}: ArticleCardProps) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const formattedDate = new Date(created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const getCategoryColor = (cat: string) => {
    const colors: Record<string, string> = {
      'Basics': 'from-blue-400 to-blue-600',
      'Advanced': 'from-purple-400 to-purple-600',
      'Career': 'from-green-400 to-green-600',
      'Relationships': 'from-pink-400 to-pink-600',
      'Health': 'from-orange-400 to-orange-600',
      'Remedies': 'from-indigo-400 to-indigo-600',
    };
    return colors[cat] || 'from-indigo-400 to-indigo-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      viewport={{ once: true }}
      className="group"
    >
      <Link to={`/article/${slug}`}>
        <div className="card h-full flex flex-col overflow-hidden hover:shadow-2xl transition-all duration-300">
          {/* Featured Image */}
          {featured_image && (
            <div className="relative h-48 bg-gradient-to-br from-slate-700 to-slate-900 overflow-hidden">
              {!imageLoaded && (
                <div className="absolute inset-0 animate-pulse bg-slate-600" />
              )}
              <motion.img
                src={featured_image}
                alt={title}
                className={`w-full h-full object-cover transition-transform duration-500 group-hover:scale-110 ${
                  imageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => setImageLoaded(true)}
              />
            </div>
          )}

          {/* Category Badge */}
          <div className="absolute top-4 left-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className={`px-3 py-1 rounded-full text-xs font-semibold text-white bg-gradient-to-r ${getCategoryColor(
                category
              )} shadow-lg`}
            >
              {category}
            </motion.div>
          </div>

          {/* Content */}
          <div className="p-6 flex flex-col flex-grow">
            {/* Title */}
            <motion.h3
              whileHover={{ color: '#6366f1' }}
              className="text-xl font-bold text-text-primary mb-3 line-clamp-2 transition-colors"
            >
              {title}
            </motion.h3>

            {/* Excerpt */}
            <p className="text-text-secondary text-sm mb-4 line-clamp-2 flex-grow">
              {excerpt}
            </p>

            {/* Meta Information */}
            <div className="flex items-center justify-between text-xs text-text-secondary pt-4 border-t border-white/10">
              <div className="flex items-center gap-2">
                <span className="font-medium">{author}</span>
                <span>•</span>
                <span>{formattedDate}</span>
              </div>
              <div className="flex items-center gap-1 text-primary">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
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
                <span>{view_count}</span>
              </div>
            </div>
          </div>

          {/* Read More Indicator */}
          <div className="px-6 pb-6">
            <motion.div
              whileHover={{ gap: '8px' }}
              className="flex items-center gap-2 text-primary font-semibold text-sm group-hover:text-secondary transition-colors"
            >
              Read More
              <motion.svg
                whileHover={{ x: 3 }}
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </motion.svg>
            </motion.div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
};

export default ArticleCard;
