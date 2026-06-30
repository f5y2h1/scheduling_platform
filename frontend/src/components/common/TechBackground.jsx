/**
 * TechBackground - Animated canvas particle background
 * Lightweight, no external dependencies beyond React
 */
import React, { useEffect, useRef } from 'react';

export default function TechBackground({ particleColor = '102,126,234', count = 60 }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1);
      canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1);
      ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
    };

    resize();
    window.addEventListener('resize', resize);

    const w = () => canvas.offsetWidth;
    const h = () => canvas.offsetHeight;

    class Particle {
      constructor() {
        this.reset();
        this.y = Math.random() * h();
      }
      reset() {
        this.x = Math.random() * w();
        this.y = -10;
        this.vx = (Math.random() - 0.5) * 0.3;
        this.vy = 0.2 + Math.random() * 0.6;
        this.r = 0.3 + Math.random() * 1.2;
        this.alpha = 0.1 + Math.random() * 0.3;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.y > h() + 10 || this.x < -10 || this.x > w() + 10) {
          this.reset();
          this.y = -10;
        }
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${particleColor},${this.alpha})`;
        ctx.fill();
      }
    }

    const particles = Array.from({ length: count }, () => new Particle());

    // Draw grid lines
    const drawGrid = () => {
      ctx.strokeStyle = `rgba(${particleColor},0.04)`;
      ctx.lineWidth = 0.5;
      const step = 60;
      for (let x = 0; x < w(); x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h());
        ctx.stroke();
      }
      for (let y = 0; y < h(); y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w(), y);
        ctx.stroke();
      }
    };

    const animate = () => {
      ctx.clearRect(0, 0, w(), h());
      drawGrid();
      particles.forEach(p => { p.update(); p.draw(); });

      // Draw connections between nearby particles
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(${particleColor},${0.06 * (1 - dist / 100)})`;
            ctx.lineWidth = 0.3;
            ctx.stroke();
          }
        }
      }
      animRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [particleColor, count]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.7,
      }}
    />
  );
}
