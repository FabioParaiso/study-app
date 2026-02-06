/**
 * Reusable metric card component for the Analytics Dashboard.
 * Displays an icon, label, and value in a consistent card layout.
 */
const MetricCard = ({ icon: Icon, iconBg, iconTextColour = 'text-white', label, value }) => (
    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl ${iconBg} ${iconTextColour} flex items-center justify-center`}>
            <Icon size={22} />
        </div>
        <div>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">{label}</p>
            <p className="text-2xl font-black text-gray-700">{value}</p>
        </div>
    </div>
);

export default MetricCard;
