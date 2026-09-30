import 'package:flutter/widgets.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

/// Lucide icon tokens (docs/DESIGN_SYSTEM.md §4).
///
/// Sizes: see `AppSizes.icon*`.
abstract final class FinoraIcons {
  // Navigation
  static const IconData home = LucideIcons.house;
  static const IconData activity = LucideIcons.arrowLeftRight;
  static const IconData stats = LucideIcons.chartPie;
  static const IconData budgets = LucideIcons.target;
  static const IconData profile = LucideIcons.user;
  static const IconData back = LucideIcons.chevronLeft;
  static const IconData forward = LucideIcons.chevronRight;
  static const IconData close = LucideIcons.x;

  // Actions
  static const IconData add = LucideIcons.plus;
  static const IconData send = LucideIcons.send;
  static const IconData scan = LucideIcons.scanLine;
  static const IconData search = LucideIcons.search;
  static const IconData filter = LucideIcons.slidersHorizontal;
  static const IconData notifications = LucideIcons.bell;
  static const IconData show = LucideIcons.eye;
  static const IconData hide = LucideIcons.eyeOff;
  static const IconData delete = LucideIcons.delete;
  static const IconData calendar = LucideIcons.calendar;
  static const IconData export = LucideIcons.download;
  static const IconData share = LucideIcons.share2;
  static const IconData ai = LucideIcons.sparkles;
  static const IconData trash = LucideIcons.trash2;
  static const IconData check = LucideIcons.check;
  static const IconData reminder = LucideIcons.bellRing;
  static const IconData addReminder = LucideIcons.bellPlus;
  static const IconData receipt = LucideIcons.receipt;
  static const IconData refresh = LucideIcons.refreshCw;
  static const IconData minus = LucideIcons.minus;
  static const IconData chevronDown = LucideIcons.chevronDown;
  static const IconData message = LucideIcons.messageCircle;
  static const IconData arrowUp = LucideIcons.arrowUp;
  static const IconData keyboard = LucideIcons.keyboard;
  static const IconData image = LucideIcons.image;
  static const IconData flash = LucideIcons.zap;
  static const IconData flashOff = LucideIcons.zapOff;
  static const IconData fileText = LucideIcons.fileText;
  static const IconData fileSheet = LucideIcons.fileSpreadsheet;
  static const IconData file = LucideIcons.file;
  static const IconData calendarClock = LucideIcons.calendarClock;
  static const IconData snowflake = LucideIcons.snowflake;
  static const IconData shapes = LucideIcons.shapes;
  static const IconData phone = LucideIcons.phone;
  static const IconData mail = LucideIcons.mail;
  static const IconData banknote = LucideIcons.banknote;
  static const IconData layers = LucideIcons.layers;

  // Money
  static const IconData wallet = LucideIcons.wallet;
  static const IconData card = LucideIcons.creditCard;
  static const IconData income = LucideIcons.arrowDownLeft;
  static const IconData expense = LucideIcons.arrowUpRight;
  static const IconData savings = LucideIcons.handCoins;
  static const IconData coins = LucideIcons.coins;
  static const IconData trendUp = LucideIcons.trendingUp;
  static const IconData trendDown = LucideIcons.trendingDown;

  // Categories
  static const IconData groceries = LucideIcons.shoppingCart;
  static const IconData food = LucideIcons.utensils;
  static const IconData transport = LucideIcons.car;
  static const IconData bills = LucideIcons.receipt;
  static const IconData health = LucideIcons.heartPulse;
  static const IconData shopping = LucideIcons.shoppingBag;
  static const IconData housing = LucideIcons.house;
  static const IconData subscriptions = LucideIcons.repeat;
  static const IconData transfer = LucideIcons.arrowLeftRight;
  static const IconData salary = LucideIcons.briefcase;
  static const IconData travel = LucideIcons.plane;
  static const IconData laptop = LucideIcons.laptop;

  // Goals
  static const IconData goalSavings = LucideIcons.handCoins;
  static const IconData goalTravel = LucideIcons.plane;
  static const IconData goalLaptop = LucideIcons.laptop;
  static const IconData goalCar = LucideIcons.car;
  static const IconData goalHouse = LucideIcons.house;
  static const IconData goalEducation = LucideIcons.graduationCap;
  static const IconData goalHeart = LucideIcons.heart;
  static const IconData goalGift = LucideIcons.gift;
  static const IconData goalSafety = LucideIcons.shieldCheck;

  // Security
  static const IconData lock = LucideIcons.lock;
  static const IconData pinCreate = LucideIcons.lockKeyhole;
  static const IconData faceId = LucideIcons.scanFace;
  static const IconData changePin = LucideIcons.keyRound;
  static const IconData autoLock = LucideIcons.timer;

  // States
  static const IconData empty = LucideIcons.checkCheck;
  static const IconData noResults = LucideIcons.searchX;
  static const IconData offline = LucideIcons.wifiOff;
  static const IconData serverError = LucideIcons.serverCrash;
  static const IconData syncError = LucideIcons.cloudOff;
  static const IconData alert = LucideIcons.circleAlert;
  static const IconData warning = LucideIcons.triangleAlert;
  static const IconData loading = LucideIcons.loaderCircle;

  // Settings
  static const IconData security = LucideIcons.shieldCheck;
  static const IconData language = LucideIcons.globe;
  static const IconData darkMode = LucideIcons.moon;
  static const IconData help = LucideIcons.circleHelp;
  static const IconData logout = LucideIcons.logOut;
  static const IconData settings = LucideIcons.settings;
}
