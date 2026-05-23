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
    title: 'Coding Practice',
    href: '/docs/category/coding-practice',
    description: (
      <>
        Patterns, problem walkthroughs, complexity notes, and interview-ready
        explanations.
      </>
    ),
  },
  {
    title: 'System Design',
    href: '/docs/category/system-design',
    description: (
      <>
        Scalable architecture primers, tradeoff checklists, and design prompts.
      </>
    ),
  },
  {
    title: 'Behavioral Prep',
    href: '/docs/category/behavioral-prep',
    description: (
      <>
        STAR story templates, leadership examples, and structured reflection.
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
