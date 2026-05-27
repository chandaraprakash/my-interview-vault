import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  href: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Data Structures',
    href: '/docs/category/data-structures',
    description: (
      <>
        Complexity cheat sheets, bit manipulation hacks, graphs, and Blind Top 75 walkthroughs.
      </>
    ),
  },
  {
    title: 'System Design',
    href: '/docs/category/system-design',
    description: (
      <>
        Scalable architecture patterns, real-world case studies, concepts, and tradeoff matrices.
      </>
    ),
  },
  {
    title: 'Behavioral Prep',
    href: '/docs/category/behavioral-prep',
    description: (
      <>
        STAR stories, leadership principles, conflict resolution, and behavioral frameworks.
      </>
    ),
  },
  {
    title: 'AI/ML',
    href: '/docs/category/ai-ml',
    description: (
      <>
        Machine learning systems design, core ML/DL concepts, and artificial intelligence roadmaps.
      </>
    ),
  },
  {
    title: 'TPM',
    href: '/docs/category/tpm',
    description: (
      <>
        Technical Program Management metrics, execution strategies, system delivery, and cross-functional leadership.
      </>
    ),
  },
  {
    title: 'Interview and Beyond',
    href: '/docs/category/interview-and-beyond',
    description: (
      <>
        Mock interview platforms, company guides (Google, Meta, OpenAI), salary negotiation, and career development.
      </>
    ),
  },
];

function Feature({title, href, description}: FeatureItem) {
  return (
    <div className="col col--4">
      <Link className={styles.featureLink} to={href}>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </Link>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
