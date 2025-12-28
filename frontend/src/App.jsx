import React, { useState } from 'react';
import { Search, History, Sparkles, Film } from 'lucide-react';
import { api } from './services/api';
import MovieTile from './components/MovieTile';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [watchHistory, setWatchHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('build'); // build, analyze, recommend

  const handleSearch = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (q.length > 2) {
      try {
        const results = await api.searchMovies(q);
        setSearchResults(results);
      } catch (err) {
        console.error("Search failed", err);
      }
    } else {
      setSearchResults([]);
    }
  };

  const addToHistory = (movie) => {
    if (!watchHistory.find(m => m.program_id === movie.program_id)) {
      setWatchHistory([...watchHistory, movie]);
    }
    setSearchResults([]); // Clear search after adding
    setSearchQuery('');
  };

  const removeFromHistory = (id) => {
    setWatchHistory(watchHistory.filter(m => m.program_id !== id));
  };

  const findCommonality = async () => {
    setLoading(true);
    setStep('analyze');
    try {
      const result = await api.identifyTheme(watchHistory);
      setAnalysis(result);
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async () => {
    if (!analysis) return;
    setLoading(true);
    setStep('recommend');
    try {
      // Use the 'detail' from the parsed theme if available, otherwise raw reasoning or prompt input
      const themeDetail = analysis.parsed_theme?.detail || analysis.reasoning;
      const results = await api.getRecommendations(themeDetail);
      setRecommendations(results);
    } catch (err) {
      console.error("Recommendation failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans selection:bg-indigo-500 selection:text-white">
      <header className="max-w-6xl mx-auto mb-12 flex items-center gap-3">
        <div className="p-3 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20">
          <Film className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          CineMatch AI
        </h1>
      </header>

      <main className="max-w-6xl mx-auto space-y-12">
        {/* Step 1: Build History */}
        <section className={`transition-opacity duration-500 ${step !== 'build' && 'opacity-50'}`}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <History className="w-6 h-6 text-indigo-400" />
              Build Your Watch History
            </h2>
            <div className="text-sm text-slate-400">{watchHistory.length} movies selected</div>
          </div>

          {/* Search Bar */}
          <div className="relative mb-8 group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-slate-400 group-focus-within:text-indigo-400 transition-colors" />
            </div>
            <input
              type="text"
              className="w-full bg-slate-800/50 border border-slate-700/50 rounded-2xl py-4 pl-12 pr-4 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all shadow-xl shadow-black/20 backdrop-blur-sm"
              placeholder="Search for movies you've watched..."
              value={searchQuery}
              onChange={handleSearch}
            />

            {/* Search Component Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-y-auto divide-y divide-slate-700/50">
                {searchResults.map(movie => (
                  <div
                    key={movie.program_id}
                    className="p-4 hover:bg-slate-700/50 cursor-pointer flex items-center gap-4 transition-colors"
                    onClick={() => addToHistory(movie)}
                  >
                    {movie.image_url && <img src={movie.image_url} alt={movie.title} className="w-12 h-16 object-cover rounded-md shadow-sm" />}
                    <div>
                      <div className="font-medium text-slate-100">{movie.title}</div>
                      <div className="text-sm text-slate-400">{movie.year}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Watch History Tiles */}
          {watchHistory.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {watchHistory.map(movie => (
                <MovieTile
                  key={movie.program_id}
                  movie={movie}
                  onRemove={() => removeFromHistory(movie.program_id)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border-2 border-dashed border-slate-800 rounded-2xl text-slate-500">
              Search and add movies to start...
            </div>
          )}

          {watchHistory.length > 0 && step === 'build' && (
            <div className="mt-8 flex justify-end">
              <button
                onClick={findCommonality}
                disabled={loading}
                className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white px-8 py-3 rounded-xl font-medium shadow-lg shadow-indigo-500/30 transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? 'Analyzing...' : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze Taste
                  </>
                )}
              </button>
            </div>
          )}
        </section>

        {/* Step 2: Analysis Result */}
        {analysis && (
          <section className="bg-slate-800/40 border border-slate-700/50 rounded-3xl p-8 backdrop-blur-sm animate-fade-in">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-emerald-400">AI Analysis</span>
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Identified Pattern</h3>
                <div className="text-xl text-teal-300 font-medium">
                  {analysis.parsed_theme?.type?.toUpperCase() || "THEME"}
                </div>
                <div className="text-3xl font-bold mt-2 text-white">
                  {analysis.parsed_theme?.detail || "Complex Pattern Detected"}
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Model Reasoning</h3>
                <div className="text-slate-300 leading-relaxed max-h-40 overflow-y-auto pr-2 custom-scrollbar">
                  {analysis.reasoning}
                </div>
              </div>
            </div>

            {step === 'analyze' && (
              <div className="mt-8 flex justify-end">
                <button
                  onClick={getRecommendations}
                  disabled={loading}
                  className="bg-white text-slate-900 hover:bg-slate-100 px-8 py-3 rounded-xl font-bold shadow-xl transition-all transform hover:scale-105 active:scale-95 flex items-center gap-2"
                >
                  Generate Recommendations
                </button>
              </div>
            )}
          </section>
        )}

        {/* Step 3: Recommendations */}
        {recommendations.length > 0 && (
          <section className="animate-fade-in-up">
            <h2 className="text-3xl font-bold mb-8 text-white flex items-center gap-3">
              <span className="w-2 h-8 bg-indigo-500 rounded-full inline-block"></span>
              You Might Also Like
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {recommendations.map(movie => (
                <MovieTile key={movie.program_id} movie={movie} variant="recommendation" />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
