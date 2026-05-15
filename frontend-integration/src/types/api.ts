export type UserRole = 'client' | 'professional' | 'admin';

export type User = {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string | null;
};

export type Category = {
  id: number;
  name: string;
  icon: string;
  description?: string | null;
};

export type Professional = {
  id: number;
  user_id: number;
  category_id: number;
  title: string;
  description: string;
  city: string;
  state: string;
  price_from: number;
  rating: number;
  reviews_count: number;
  whatsapp?: string | null;
  is_featured: boolean;
  image?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  user: User;
  category: Category;
};
