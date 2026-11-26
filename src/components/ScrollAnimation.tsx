import { motion, useInView } from 'framer-motion';
import { useRef, type ReactNode } from 'react';

interface ScrollAnimationProps {
  children: ReactNode;
  animation?: 'fadeIn' | 'slideUp' | 'slideLeft' | 'slideRight' | 'scale';
  delay?: number;
  duration?: number;
  className?: string;
  threshold?: number;
  once?: boolean;
}

const scrollAnimations = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  },
  slideUp: {
    hidden: { opacity: 0, y: 100 },
    visible: { opacity: 1, y: 0 }
  },
  slideLeft: {
    hidden: { opacity: 0, x: 100 },
    visible: { opacity: 1, x: 0 }
  },
  slideRight: {
    hidden: { opacity: 0, x: -100 },
    visible: { opacity: 1, x: 0 }
  },
  scale: {
    hidden: { opacity: 0, scale: 0.5 },
    visible: { opacity: 1, scale: 1 }
  }
};

export default function ScrollAnimation({
  children,
  animation = 'fadeIn',
  delay = 0,
  duration = 0.8,
  className = '',
  threshold = 0.2,
  once = true
}: ScrollAnimationProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { 
    threshold,
    once
  });

  return (
    <motion.div
      ref={ref}
      variants={scrollAnimations[animation]}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      transition={{
        duration,
        delay,
        ease: "easeOut"
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}