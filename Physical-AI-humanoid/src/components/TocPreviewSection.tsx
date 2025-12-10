import React, { useEffect } from 'react';
import Link from '@docusaurus/Link';
import clsx from 'clsx';
import styles from './TocPreviewSection.module.css';

type ChapterItem = {
  number: string;
  title: string;
  lessons: number;
};

const ChapterList: ChapterItem[] = [
  { number: 'Chapter 01', title: 'Introduction to Physical AI and Humanoid Robotics', lessons: 4 },
  { number: 'Chapter 02', title: 'Fundamentals of Robotics and AI', lessons: 4 },
  { number: 'Chapter 03', title: 'Perception Systems for Humanoid Robots', lessons: 4 },
  { number: 'Chapter 04', title: 'Motion Planning and Control', lessons: 4 },
  { number: 'Chapter 05', title: 'Learning and Adaptation in Robotics', lessons: 4 },
  { number: 'Chapter 06', title: 'Human-Robot Interaction and Communication', lessons: 4 },
];

const TocPreviewSection = () => {
  useEffect(() => {
    const handleScroll = () => {
      const elements = document.querySelectorAll('.scroll-reveal');
      elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;

        if (elementTop < window.innerHeight - elementVisible) {
          element.classList.add('visible');
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check on load

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section className={clsx(styles.tocPreview, 'homepage-section', 'scroll-reveal')}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <h2 className={clsx(styles.sectionTitle, 'hover-lift')}>Table of Contents Preview</h2>
            <p className={styles.sectionDescription}>
              Explore the comprehensive curriculum designed for mastering Physical AI and Humanoid Robotics
            </p>
          </div>
        </div>
        <div className="row">
          <div className="col col--8">
            <div className={clsx('toc-preview', styles.tocList)}>
              {ChapterList.map((chapter, idx) => (
                <div key={idx} className={clsx(styles.chapterItem, 'scroll-reveal')} style={{ animationDelay: `${idx * 0.05}s` }}>
                  <div className={styles.chapterNumber}>{chapter.number}</div>
                  <div className={styles.chapterContent}>
                    <h3 className={styles.chapterTitle}>{chapter.title}</h3>
                    <div className={styles.chapterMeta}>
                      <span className={styles.lessonCount}>{chapter.lessons} lessons</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="col col--4">
            <div className={clsx(styles.tocSidebar, 'scroll-reveal')} style={{ animationDelay: '0.3s' }}>
              <div className={styles.sidebarTitle}>Course Overview</div>
              <div className={styles.sidebarContent}>
                <div className={clsx(styles.statItem, 'scroll-reveal')} style={{ animationDelay: '0.4s' }}>
                  <div className={styles.statNumber}>12</div>
                  <div className={styles.statLabel}>Chapters</div>
                </div>
                <div className={clsx(styles.statItem, 'scroll-reveal')} style={{ animationDelay: '0.5s' }}>
                  <div className={styles.statNumber}>48</div>
                  <div className={styles.statLabel}>Lessons</div>
                </div>
                <div className={clsx(styles.statItem, 'scroll-reveal')} style={{ animationDelay: '0.6s' }}>
                  <div className={styles.statNumber}>15+</div>
                  <div className={styles.statLabel}>Projects</div>
                </div>
                <div className={clsx(styles.statItem, 'scroll-reveal')} style={{ animationDelay: '0.7s' }}>
                  <div className={styles.statNumber}>100+</div>
                  <div className={styles.statLabel}>Examples</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col col--12">
            <div className={clsx(styles.ctaContainer, 'glow-effect')}>
              <Link
                className={clsx('button button--primary button--lg button--custom', styles.viewAllButton, 'pulse-animation')}
                to="/chapters/chapter-01/lesson-01">
                View All Chapters
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TocPreviewSection;