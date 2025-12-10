import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import styles from './about.module.css';

const AboutPage = () => {
  return (
    <Layout
      title="About the Author"
      description="Learn more about Muhib, the creator of the Physical AI & Humanoid Robotics Course">
      <main className={clsx('container', 'padding-vert--lg')}>
        <div className="row">
          <div className="col col--8 col--offset-2">
            <div className={clsx('hero', styles.aboutHero)} style={{display : 'flex' , justifyContent : 'center' , alignItems : 'center'}}>
              <div className="hero__title" style={{ textAlign: 'center' }}>
                About the Author
              </div>
            </div>
            <div className={clsx('margin-vert--lg', styles.aboutContent)}>
              <div className={styles.profileSection}>
                <div className={styles.profileImage}>
                  <img
                    src="/img/mypic.png"
                    alt="Muhib - Author of Physical AI & Humanoid Robotics Course"
                    className={styles.profilePic}
                  />
                </div>

                <div className={styles.profileInfo}>
                  <h2>Muhib Ali Siddiqui</h2>
                  <p className={styles.role}>UI/UX + Fullstack Developer</p>

                  <div className={styles.bio}>
                    <p>
                      Muhib Ali Siddiqui is a passionate developer with expertise in both UI/UX design and fullstack development.
                      With a strong background in creating intuitive user experiences and robust backend systems,
                      Muhib has dedicated his career to building innovative solutions in the field of Physical AI and Humanoid Robotics.
                    </p>

                    <p>
                      His work focuses on making complex technologies accessible and understandable to a broader audience.
                      Through this course, he aims to share his knowledge and inspire the next generation of developers
                      and researchers in the field of robotics and artificial intelligence.
                    </p>
                  </div>

                  <div className={styles.skills}>
                    <h3>Skills & Expertise</h3>
                    <ul>
                      <li>UI/UX Design & Prototyping</li>
                      <li>Next.js and Typescript</li>
                      <li>Fullstack Web Development</li>
                      <li>Physical AI & Robotics</li>
                      <li>Humanoid Robot Programming</li>
                      <li>Machine Learning & Deep Learning</li>
                      <li>3D Modeling & Simulation</li>
                    </ul>
                  </div>

                  <div className={styles.connect}>
                    <h3>Connect</h3>
                    <p>Feel free to reach out for collaborations, questions, or just to say hello!</p>
                    <div className={styles.socialLinks}>
                      <a href="https://github.com/muhibali123" className={styles.socialLink}>
                        GitHub
                      </a>
                      <a href="https://www.linkedin.com/in/muhib-ali-siddiqui-5424382b5/" className={styles.socialLink}>
                        Linkedin
                      </a>
                      <a href="https://muhibsiddiqui58@gmail.com" className={styles.socialLink}>
                        Email
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
};

export default AboutPage;