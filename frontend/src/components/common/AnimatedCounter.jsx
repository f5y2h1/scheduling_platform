import { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';

/**
 * AnimatedCounter — counts up from 0 to target when visible
 */
export default function AnimatedCounter({ value = 0, duration = 1.2, suffix = '', prefix = '' }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
  const animRef = useRef(null);

  useEffect(() => {
    if (!inView) return;
    const target = Number(value) || 0;
    const start = performance.now();

    const step = (now) => {
      const elapsed = (now - start) / 1000;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutExpo
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setDisplay(Math.round(eased * target));
      if (progress < 1) {
        animRef.current = requestAnimationFrame(step);
      }
    };

    animRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animRef.current);
  }, [inView, value, duration]);

  return (
    <span ref={ref}>
      {prefix}{display.toLocaleString()}{suffix}
    </span>
  );
}
