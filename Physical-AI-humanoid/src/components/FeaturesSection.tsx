import React, { JSX, useEffect } from 'react';
import clsx from 'clsx';
import styles from './FeaturesSection.module.css';

type FeatureItem = {
  title: string;
  description: JSX.Element;
  icon: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Advanced AI Integration',
    icon: '🤖',
    description: (
      <>
        Learn how to integrate cutting-edge AI algorithms with humanoid robots for intelligent behavior and decision making.
      </>
    ),
  },
  {
    title: 'Real-World Applications',
    icon: '🌍',
    description: (
      <>
        Explore practical applications of humanoid robotics in healthcare, manufacturing, education, and service industries.
      </>
    ),
  },
  {
    title: 'Hands-On Projects',
    icon: '🛠️',
    description: (
      <>
        Build and program your own humanoid robots with step-by-step projects designed for all skill levels.
      </>
    ),
  },
  {
    title: 'Cutting-Edge Research',
    icon: '🔬',
    description: (
      <>
        Stay updated with the latest research in physical AI, biomechanics, and human-robot interaction.
      </>
    ),
  },
];

const FeaturesSection = () => {
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
    <section className={clsx(styles.features, 'homepage-section', 'scroll-reveal')}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <h2 className={clsx(styles.sectionTitle, 'hover-lift')}>What You'll Learn</h2>
            <p className={styles.sectionDescription}>
              Comprehensive coverage of Physical AI and Humanoid Robotics concepts with practical applications
            </p>
          </div>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <div key={idx} className="col col--3">
              <div className={clsx('feature-card', styles.featureCard, 'scroll-reveal')} style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className={clsx(styles.featureIcon, 'icon-hover')}>{props.icon}</div>
                <h3 className={styles.featureTitle}>{props.title}</h3>
                <p className={styles.featureDescription}>{props.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;