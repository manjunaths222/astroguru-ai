import Navbar from '@/components/layout/Navbar';
import ArticlesSection from '@/components/articles/ArticlesSection';

const ArticlesPage = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <Navbar />
      <ArticlesSection
        title="All Articles"
        limit={100}
        showCategories={true}
      />
    </div>
  );
};

export default ArticlesPage;
