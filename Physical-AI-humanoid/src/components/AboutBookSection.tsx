import React, { useEffect } from 'react';
import clsx from 'clsx';
import styles from './AboutBookSection.module.css';

const AboutBookSection = () => {
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
    <section className={clsx(styles.aboutBook, 'homepage-section--dark', 'scroll-reveal')}>
      <div className="container">
        <div className="row">
          <div className="col col--6">
            <div className={clsx(styles.aboutImage, 'floating-element')}>
              <div className={styles.bookCover}>
                <div className={styles.bookSpine}></div>
                <div className={styles.bookFront}>
                  <div className={styles.bookTitle}>Physical AI & Humanoid Robotics</div>
                  <div className={styles.bookSubtitle}>A Comprehensive Guide</div>
                </div>
              </div>
            </div>
          </div>
          <div className="col col--6">
            <div className={styles.aboutContent}>
              <h2 className={clsx(styles.sectionTitle, 'hover-lift')}>About the Book</h2>
              <p className={styles.sectionDescription}>
                This comprehensive course covers everything you need to know about Physical AI and Humanoid Robotics,
                from fundamental concepts to advanced implementations. Whether you're a beginner or an experienced
                developer, you'll find practical examples, hands-on projects, and cutting-edge research insights.
              </p>
              <div className={styles.keyPoints}>
                <div className={clsx(styles.keyPoint, 'scroll-reveal')} style={{ animationDelay: '0.1s' }}>
                  <div className={styles.keyPointIcon}>✓</div>
                  <div className={styles.keyPointText}>Step-by-step tutorials for building humanoid robots</div>
                </div>
                <div className={clsx(styles.keyPoint, 'scroll-reveal')} style={{ animationDelay: '0.2s' }}>
                  <div className={styles.keyPointIcon}>✓</div>
                  <div className={styles.keyPointText}>Real-world applications and case studies</div>
                </div>
                <div className={clsx(styles.keyPoint, 'scroll-reveal')} style={{ animationDelay: '0.3s' }}>
                  <div className={styles.keyPointIcon}>✓</div>
                  <div className={styles.keyPointText}>Advanced AI integration techniques</div>
                </div>
                <div className={clsx(styles.keyPoint, 'scroll-reveal')} style={{ animationDelay: '0.4s' }}>
                  <div className={styles.keyPointIcon}>✓</div>
                  <div className={styles.keyPointText}>Ethical considerations and safety principles</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutBookSection;