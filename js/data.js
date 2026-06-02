/**
 * RADIO DVA — Data & Configuration
 * 50/50 Russian & World hits — AI-powered radio
 */

const RADIO_CONFIG = {
    name: 'RADIO DVA',
    tagline: 'Двойная Волна',
    streamUrl: 'http://localhost:8888/stream',
    streamType: 'audio/mpeg',
    api: '/api',
    aiHosts: [
        { name: 'Алекс', style: 'энергичный', emoji: '🎧' },
        { name: 'Лина', style: 'плавная', emoji: '🎙️' }
    ]
};

const TRACK_HISTORY = [
    { title: 'Поначалу', artist: 'Баста', time: '2 мин назад', flag: '🇷🇺' },
    { title: 'Blinding Lights', artist: 'The Weeknd', time: '6 мин назад', flag: '🌍' },
    { title: 'Я твоя', artist: 'Anna Asti', time: '10 мин назад', flag: '🇷🇺' },
    { title: 'Flowers', artist: 'Miley Cyrus', time: '14 мин назад', flag: '🌍' },
    { title: 'Плакала', artist: 'Kazka', time: '19 мин назад', flag: '🇷🇺' },
    { title: 'As It Was', artist: 'Harry Styles', time: '23 мин назад', flag: '🌍' },
    { title: 'Малиновая Лада', artist: 'Gayazovs Brothers', time: '27 мин назад', flag: '🇷🇺' },
    { title: 'Shape of You', artist: 'Ed Sheeran', time: '31 мин назад', flag: '🌍' },
    { title: 'Squad', artist: 'Miyagi & Andy Panda', time: '35 мин назад', flag: '🇷🇺' },
    { title: 'Starboy', artist: 'The Weeknd', time: '39 мин назад', flag: '🌍' },
];

const CURRENT_TRACK = {
    title: 'Prada',
    artist: 'cassö, RAYE, D-Block Europe',
    cover: null,
    flag: '🌍',
    host: 'Алекс'
};
