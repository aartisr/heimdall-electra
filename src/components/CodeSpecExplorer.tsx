import React, { useState } from 'react';
import {
  FileCode,
  FileText,
  Search,
  Copy,
  Check,
  ExternalLink,
  BookOpen,
  Code2,
  Layers,
  Terminal,
} from 'lucide-react';
import { SPEC_FILES, SpecFile } from '../data/specData';
import { REPO_METADATA } from '../data/evaluationData';

export const CodeSpecExplorer: React.FC = () => {
  const [selectedFileId, setSelectedFileId] = useState<string>('claim_gov');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  const selectedFile =
    SPEC_FILES.find((f) => f.id === selectedFileId) || SPEC_FILES[0];

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredFiles = SPEC_FILES.filter((f) =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    f.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Repository Artifact & Code Explorer</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Formal Specifications & Core Solver Kernels
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Inspect the authentic mathematical contracts, epistemic claim governance rules, and
              metamorphic physics test harnesses from the <strong className="text-white">{REPO_METADATA.fullName}</strong> repository.
            </p>
          </div>

          <a
            href={REPO_METADATA.url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl border border-slate-700 text-xs font-medium inline-flex items-center gap-2 transition-colors self-start sm:self-auto"
          >
            <Code2 className="w-4 h-4 text-cyan-400" />
            <span>View 302 Files on GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Explorer Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Sidebar: File Directory */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search specifications & code..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-1 pt-1">
            Core Specifications ({filteredFiles.length})
          </div>

          <div className="space-y-1.5">
            {filteredFiles.map((file) => {
              const isSelected = file.id === selectedFile.id;
              return (
                <button
                  key={file.id}
                  onClick={() => setSelectedFileId(file.id)}
                  className={`w-full text-left p-3 rounded-lg text-xs transition-all flex items-start gap-2.5 border ${
                    isSelected
                      ? 'bg-cyan-500/10 border-cyan-500/40 text-white shadow-sm'
                      : 'bg-slate-950/40 border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  {file.language === 'python' ? (
                    <Terminal
                      className={`w-4 h-4 mt-0.5 shrink-0 ${
                        isSelected ? 'text-cyan-400' : 'text-blue-400'
                      }`}
                    />
                  ) : (
                    <FileText
                      className={`w-4 h-4 mt-0.5 shrink-0 ${
                        isSelected ? 'text-purple-400' : 'text-slate-500'
                      }`}
                    />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <div className="font-mono font-bold truncate">{file.name}</div>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-sans">
                        {file.category}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 truncate mt-0.5">
                      {file.path}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Code & Markdown Viewer */}
        <div className="lg:col-span-8 bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col">
          {/* Top Bar */}
          <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 min-w-0">
              <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
              <div className="min-w-0">
                <div className="text-xs font-mono font-bold text-white truncate">
                  {selectedFile.path}
                </div>
                <div className="text-[11px] text-slate-400 truncate">
                  {selectedFile.description}
                </div>
              </div>
            </div>

            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition-colors flex items-center gap-1.5 shrink-0 border border-slate-700"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Code</span>
                </>
              )}
            </button>
          </div>

          {/* Code Window */}
          <div className="p-4 sm:p-6 overflow-x-auto max-h-[620px] font-mono text-xs text-slate-200 leading-relaxed bg-slate-950">
            <pre className="whitespace-pre">
              {selectedFile.content.split('\n').map((line, idx) => (
                <div key={idx} className="table-row">
                  <span className="table-cell pr-4 text-right select-none text-slate-600 font-mono text-[11px]">
                    {idx + 1}
                  </span>
                  <span className="table-cell">
                    {line.startsWith('#') ? (
                      <span className="text-purple-400 font-bold">{line}</span>
                    ) : line.startsWith('def ') || line.startsWith('class ') ? (
                      <span className="text-cyan-300 font-semibold">{line}</span>
                    ) : line.startsWith('import ') || line.startsWith('from ') ? (
                      <span className="text-amber-300">{line}</span>
                    ) : line.includes('"""') || line.includes('//') ? (
                      <span className="text-slate-500 italic">{line}</span>
                    ) : (
                      line
                    )}
                  </span>
                </div>
              ))}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
