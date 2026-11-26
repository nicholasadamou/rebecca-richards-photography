import { motion, type Variants } from 'framer-motion';
import type { ReactNode } from 'react';

interface AnimatedContainerProps {
  children: ReactNode;
  animation?: 'fadeIn' | 'slideUp' | 'slideDown' | 'slideLeft' | 'slideRight' | 'scale' | 'stagger';
  delay?: number;
  duration?: number;
  className?: string;
}

const animations: Record<string, Variants> = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  },
  slideUp: {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0 }
  },
  slideDown: {
    hidden: { opacity: 0, y: -50 },
    visible: { opacity: 1, y: 0 }
  },
  slideLeft: {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0 }
  },
  slideRight: {
    hidden: { opacity: 0, x: -50 },
    visible: { opacity: 1, x: 0 }
  },
  scale: {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 }
  },
  stagger: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }
};

export default function AnimatedContainer({ 
  children, 
  animation = 'fadeIn', 
  delay = 0, 
  duration = 0.6,
  className = ''
}: AnimatedContainerProps) {
  return (
    <motion.div
      variants={animations[animation]}
      initial="hidden"
      animate="visible"
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