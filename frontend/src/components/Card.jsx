export default function Card({ title, icon: Icon, action, children, className = '' }) {
  return (
    <section
      className={`bg-tg-section-bg rounded-card p-4 shadow-card border border-white/5 ${className}`}
    >
      {(title || Icon || action) && (
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {Icon && (
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-brand-lime/10 text-brand-lime shrink-0">
                <Icon size={16} strokeWidth={2.25} />
              </span>
            )}
            {title && (
              <h2 className="text-sm font-semibold tracking-wide text-tg-text uppercase">
                {title}
              </h2>
            )}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}
