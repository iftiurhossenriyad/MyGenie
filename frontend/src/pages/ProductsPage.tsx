import { useState, useEffect, type FormEvent } from 'react';
import Layout from '../components/Layout';
import { useWorkspace } from '../context/WorkspaceContext';
import { productsApi } from '../lib/business';
import type { Product } from '../lib/business';

export default function ProductsPage() {
  const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [stockProduct, setStockProduct] = useState<Product | null>(null);
  const [stockChange, setStockChange] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sku: '',
    price: '0',
    stock_quantity: '0',
    is_available: true,
  });

  const loadProducts = async () => {
    if (!currentWorkspace) return;
    try {
      setLoading(true);
      const data = await productsApi.list(currentWorkspace.id);
      setProducts(data);
    } catch {
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!currentWorkspace) return;

    let active = true;

    const load = async () => {
      try {
        const data = await productsApi.list(currentWorkspace.id);
        if (active) setProducts(data);
      } catch {
        if (active) setError('Failed to load products');
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [currentWorkspace]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentWorkspace || !formData.name.trim()) return;

    try {
      await productsApi.create(currentWorkspace.id, {
        name: formData.name,
        description: formData.description,
        sku: formData.sku,
        price: parseFloat(formData.price),
        stock_quantity: parseInt(formData.stock_quantity),
        is_available: formData.is_available,
        currency: 'BDT',
      });
      setFormData({
        name: '',
        description: '',
        sku: '',
        price: '0',
        stock_quantity: '0',
        is_available: true,
      });
      setShowForm(false);
      loadProducts();
    } catch {
      setError('Failed to create product');
    }
  };

  const handleAdjustStock = async (product: Product) => {
    const change = Number(stockChange);
    if (!Number.isInteger(change) || change === 0) {
      setError('Enter a non-zero whole number to adjust stock.');
      return;
    }

    try {
      await productsApi.adjustStock(product.id, change);
      setStockProduct(null);
      setStockChange('');
      setError('');
      await loadProducts();
    } catch {
      setError('Failed to adjust stock');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this product?')) return;
    try {
      await productsApi.delete(id);
      loadProducts();
    } catch {
      setError('Failed to delete product');
    }
  };

  if (workspaceLoading) {
    return (
      <Layout title="Products">
        <div className="text-center text-gray-500 py-8">Loading...</div>
      </Layout>
    );
  }

  if (!currentWorkspace || currentWorkspace.type !== 'business') {
    return (
      <Layout title="Products">
        <div className="card text-center py-12">
          <p className="text-gray-500">Please select a business workspace.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Products">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-navy">Products</h2>
            <p className="text-sm text-gray-500 bengali">আপনার পণ্যসমূহ</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary"
          >
            {showForm ? 'Cancel' : '+ New Product'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {stockProduct && (
          <div className="card">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleAdjustStock(stockProduct);
              }}
              className="space-y-4"
            >
              <div>
                <h3 className="text-lg font-semibold text-navy">Adjust stock</h3>
                <p className="text-sm text-gray-500">
                  {stockProduct.name} — current stock: {stockProduct.stock_quantity}
                </p>
              </div>
              <div>
                <label className="label" htmlFor="stock-change">
                  Quantity change (for example, 5 or -3)
                </label>
                <input
                  id="stock-change"
                  type="number"
                  step="1"
                  className="input"
                  value={stockChange}
                  onChange={(event) => setStockChange(event.target.value)}
                  required
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary">
                  Save adjustment
                </button>
                <button
                  type="button"
                  className="btn"
                  onClick={() => {
                    setStockProduct(null);
                    setStockChange('');
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Create Form */}
        {showForm && (
          <div className="card">
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="label">Product Name *</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    placeholder="Product name"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="label">Description</label>
                  <textarea
                    className="input"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    rows={2}
                  />
                </div>
                <div>
                  <label className="label">SKU (Optional)</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.sku}
                    onChange={(e) =>
                      setFormData({ ...formData, sku: e.target.value })
                    }
                    placeholder="SKU-001"
                  />
                </div>
                <div>
                  <label className="label">Price (BDT) *</label>
                  <input
                    type="number"
                    className="input"
                    value={formData.price}
                    onChange={(e) =>
                      setFormData({ ...formData, price: e.target.value })
                    }
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
                <div>
                  <label className="label">Stock Quantity</label>
                  <input
                    type="number"
                    className="input"
                    value={formData.stock_quantity}
                    onChange={(e) =>
                      setFormData({ ...formData, stock_quantity: e.target.value })
                    }
                    min="0"
                  />
                </div>
                <div className="flex items-center">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_available}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          is_available: e.target.checked,
                        })
                      }
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Available for sale</span>
                  </label>
                </div>
              </div>
              <button type="submit" className="btn btn-primary">
                Create Product
              </button>
            </form>
          </div>
        )}

        {/* Products List */}
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading...</div>
        ) : products.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 mb-4">No products yet</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-gold"
            >
              Add your first product
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map((product) => (
              <div key={product.id} className="card">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-navy">
                    {product.name}
                  </h3>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      product.is_available
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {product.is_available ? 'Available' : 'Unavailable'}
                  </span>
                </div>

                {product.description && (
                  <p className="text-gray-600 text-sm mb-3">
                    {product.description}
                  </p>
                )}

                <div className="space-y-1 text-sm mb-3">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Price:</span>
                    <span className="font-semibold text-navy">
                      {product.currency} {product.price}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stock:</span>
                    <span
                      className={`font-semibold ${
                        product.stock_quantity === 0
                          ? 'text-red-600'
                          : 'text-navy'
                      }`}
                    >
                      {product.stock_quantity}
                    </span>
                  </div>
                  {product.sku && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">SKU:</span>
                      <span className="text-gray-700 text-xs">
                        {product.sku}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 pt-3 border-t border-gray-100">
                  <button
                    onClick={() => {
                      setStockProduct(product);
                      setStockChange('');
                      setError('');
                    }}
                    className="flex-1 text-xs px-2 py-1 bg-navy text-white rounded hover:bg-navy-dark"
                  >
                    Adjust Stock
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="text-xs px-3 py-1 text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}