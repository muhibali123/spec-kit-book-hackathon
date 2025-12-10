import React, { useEffect } from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import clsx from 'clsx';
import styles from './HeroSection.module.css';

const HeroSection = () => {
  const {siteConfig} = useDocusaurusContext();

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

    // Create floating particles
    const createParticles = () => {
      const hero = document.querySelector(`.${styles.hero}`);
      if (!hero) return;

      // Clear existing particles
      const existingParticles = hero.querySelectorAll('.hero-particle');
      existingParticles.forEach(p => p.remove());

      // Create new particles
      for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.className = 'hero-particle';

        // Random size and position
        const size = Math.random() * 20 + 5;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const delay = Math.random() * 6;
        const duration = 4 + Math.random() * 4;

        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;

        hero.appendChild(particle);
      }
    };

    createParticles();
    window.addEventListener('resize', createParticles);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', createParticles);
    };
  }, []);

  return (
    <section className={clsx(styles.hero, 'hero-gradient', 'scroll-reveal', 'hero-parallax')}>
      <div className="hero-spotlight"></div>
      <div className="hero-particles" aria-hidden="true"></div>
      <div className="hero-wave"></div>
      <div className="container">
        <div className="row">
          <div className="col col--6">
            <h1 className={clsx(styles.heroTitle, 'hover-lift', 'hero-title-glow')}>
              <span className="typewriter-text">
                <span className="text-line">Physical AI &amp;</span>
                <br />
                <span className="text-line">Humanoid Robotics</span>
              </span>
            </h1>
            <p className={clsx(styles.heroSubtitle, 'scale-hover')}>{siteConfig.tagline}</p>
            <div className={clsx(styles.buttons, 'glow-effect')}>
              <Link
                className={clsx('button button--primary button--lg button--custom button-ripple', styles.button, 'pulse-animation')}
                to="/chapters/chapter-01/lesson-01">
                Read Book
              </Link>
            </div>
          </div>
          <div className="col col--6">
            <div className={clsx(styles.heroImage, 'floating-element', 'scale-hover')}>
              <div className={styles.robotAnimation}>
                {/* Robot parts */}
                <div className={clsx(styles.robotBody, 'icon-hover')}></div>
                <div className={clsx(styles.robotHead, 'icon-hover')}></div>

                {/* Robot face details */}
                <div className={clsx(styles.robotFace, 'icon-hover')}></div>
                <div className={clsx(styles.robotEyeLeft, 'icon-hover')}></div>
                <div className={clsx(styles.robotEyeRight, 'icon-hover')}></div>
                <div className={clsx(styles.robotMouth, 'icon-hover')}></div>

                {/* Robot arms with message bubble on right arm */}
                <div className={clsx(styles.robotLeftArm, 'icon-hover')}></div>
                <div className={clsx(styles.robotRightArm, 'icon-hover')}>
                  {/* Message bubble positioned near the right hand */}
                  <div className={styles.messageBubble}>
                    <div className={styles.messageText}>What can I do for you?</div>
                    <div className={styles.messageArrow}></div>
                  </div>
                </div>

                {/* Robot legs */}
                <div className={clsx(styles.robotLeftLeg, 'icon-hover')}></div>
                <div className={clsx(styles.robotRightLeg, 'icon-hover')}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;