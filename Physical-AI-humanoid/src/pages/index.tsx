import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import AboutBookSection from '../components/AboutBookSection';
import TocPreviewSection from '../components/TocPreviewSection';
import Heading from '@theme/Heading';

import styles from './index.module.css';

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Comprehensive educational resource for Physical AI and Humanoid Robotics">
      <HeroSection />
      <FeaturesSection />
      <AboutBookSection />
      <TocPreviewSection />
    </Layout>
  );
}