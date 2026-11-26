interface AlbumCardProps {
  album: {
    title: string;
    slug: { current: string };
    coverImage?: any;
    albumType: string;
    date?: string;
    imageCount?: number;
  };
  coverImageUrl: string | null;
  albumTypeDisplay: string;
  formattedDate: string;
}

// Heart SVG icon component
function HeartIcon({ size = 24, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
    </svg>
  );
}

// Camera/Photo SVG icon component
function PhotoIcon({ size = 24, className = '' }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
      <circle cx="9" cy="9" r="2"></circle>
      <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
    </svg>
  );
}

export default function AlbumCard({
  album,
  coverImageUrl,
  albumTypeDisplay,
  formattedDate,
}: AlbumCardProps) {
  return (
    <a href={`/albums/${album.slug.current}`} className="group block">
      <div className="bg-white rounded-sm shadow-sm overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="aspect-[4/3] overflow-hidden">
          {coverImageUrl ? (
            <img
              src={coverImageUrl}
              alt={`${album.title} Album Cover`}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <HeartIcon size={48} className="text-gray-400" />
            </div>
          )}
        </div>
        <div className="p-6">
          <h3 className="text-xl font-light text-gray-900 mb-2 tracking-wide">
            {album.title}
          </h3>
          <p className="text-gray-600 font-light mb-2">{albumTypeDisplay}</p>
          <p className="text-sm text-gray-500 font-light mb-4">
            {formattedDate && <span>{formattedDate}</span>}
            {album.imageCount && album.imageCount > 0 && (
              <span className="flex items-center">
                <PhotoIcon size={14} className="mr-1" />
                {album.imageCount} photos
              </span>
            )}
          </p>
          <div className="flex items-center text-rose-400 font-light">
            <HeartIcon size={16} className="mr-2" />
            <span>View Album</span>
          </div>
        </div>
      </div>
    </a>
  );
}
