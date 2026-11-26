import React from 'react';
import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface StaggeredGridProps {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
  initialDelay?: number;
}

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: {
    opacity: 0,
    y: 50,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut",
    },
  },
};

export default function StaggeredGrid({ 
  children, 
  className = '', 
  staggerDelay = 0.1,
  initialDelay = 0 
}: StaggeredGridProps) {
  // Convert children to array if it isn't already
  const childrenArray = React.Children.toArray(children);
  
  return (
    <>
      {childrenArray.map((child, index) => (
        <motion.div 
          key={index} 
          variants={itemVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          transition={{
            delay: initialDelay + (index * staggerDelay)
          }}
          className={className}
        >
          {child}
        </motion.div>
      ))}
    </>
  );
}
