import { PartyPopper, Star, CheckCircle, Trophy, Flame, Brain, Search, Lightbulb, Eye, BicepsFlexed } from 'lucide-react';

const icons = {
    PartyPopper, Star, CheckCircle, Trophy, Flame, Brain, Search, Lightbulb, Eye, BicepsFlexed
};

const FeedbackIcon = ({ iconName, className }) => {
    const Icon = icons[iconName];
    if (!Icon) return null;
    return <Icon className={className} />;
};

export default FeedbackIcon;
