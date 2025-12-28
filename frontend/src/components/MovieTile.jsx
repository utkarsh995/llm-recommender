import React from 'react';
import { X, Star } from 'lucide-react';

const MovieTile = ({ movie, onRemove, variant = 'history' }) => {
    return (
        <div className="group relative bg-slate-800 rounded-xl overflow-hidden shadow-lg hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 transform hover:-translate-y-1">
            {/* Image / Placeholder */}
            <div className="aspect-[2/3] bg-slate-700 relative overflow-hidden">
                {movie.image_url ? (
                    <img
                        src={movie.image_url}
                        alt={movie.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-500">
                        <span className="text-4xl">🎬</span>
                    </div>
                )}

                {/* Overlay for Recommendation Rating or Remove */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-between p-4">
                    <div className="flex justify-end">
                        {variant === 'history' && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onRemove(); }}
                                className="bg-red-500/20 hover:bg-red-500 text-red-200 hover:text-white p-2 rounded-full backdrop-blur-md transition-all"
                            >
                                <X size={16} />
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Info */}
            <div className="p-4">
                <h3 className="font-bold text-slate-100 truncate text-lg group-hover:text-indigo-400 transition-colors" title={movie.title}>
                    {movie.title}
                </h3>
                <div className="flex items-center justify-between mt-1">
                    <span className="text-sm text-slate-400 font-medium">{movie.year}</span>
                </div>
            </div>
        </div>
    );
};

export default MovieTile;
