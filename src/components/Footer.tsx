import React from 'react';
import { ShieldCheck, ExternalLink, Github, Heart } from 'lucide-react';
import { REPO_METADATA } from '../data/evaluationData';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 mt-16 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>
            Independent Technical Evaluation of <strong className="text-white">{REPO_METADATA.fullName}</strong>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span>Overall Score: <strong className="text-cyan-400 font-mono">8.9 / 10 (Grade A)</strong></span>
          <a
            href={REPO_METADATA.url}
            target="_blank"
            rel="noreferrer"
            className="hover:text-cyan-400 transition-colors inline-flex items-center gap-1"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </footer>
  );
};
