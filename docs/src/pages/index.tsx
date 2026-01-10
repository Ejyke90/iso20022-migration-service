import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started - 5min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="SWIFT MT to ISO 20022 MX conversion service">
      <HomepageHeader />
      <main>
        <div className="container">
          <div className="row">
            <div className="col col--6">
              <h2>SWIFT MT to ISO 20022 MX</h2>
              <p>Convert legacy SWIFT MT messages to modern ISO 20022 XML formats with our comprehensive conversion service.</p>
            </div>
            <div className="col col--6">
              <h2>Production Ready</h2>
              <p>Built with FastAPI, Pydantic models, and comprehensive testing for reliable financial message processing.</p>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
