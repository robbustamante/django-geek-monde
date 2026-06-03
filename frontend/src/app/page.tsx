import Image from "next/image";

// Fetch data from Django API
async function getProducts() {
  try {
    // Usamos no-store para que siempre intente traer los datos más recientes en desarrollo
    const res = await fetch('http://127.0.0.1:8000/api/v1/catalog/products/', { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to fetch data: ${res.status}`);
    }
    return res.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    return null;
  }
}

export default async function Home() {
  const data = await getProducts();
  
  // Django REST Framework Pagination by default uses `results`
  const products = data?.results || [];

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans text-zinc-900 dark:text-zinc-50 p-8 sm:p-12">
      <header className="mb-12 border-b border-zinc-200 dark:border-zinc-800 pb-8">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent mb-4">
          Geek Monde
        </h1>
        <p className="text-lg text-zinc-600 dark:text-zinc-400 flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${data ? 'bg-green-400' : 'bg-red-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${data ? 'bg-green-500' : 'bg-red-500'}`}></span>
          </span>
          {data ? 'Conectado exitosamente con Django' : 'Esperando conexión con el backend de Django'}
        </p>
      </header>
      
      <main className="flex-1 max-w-7xl mx-auto w-full">
        <h2 className="text-2xl font-semibold mb-8 flex items-center gap-3">
          Explorar Catálogo
        </h2>
        
        {!data ? (
          <div className="p-8 bg-white dark:bg-zinc-900 rounded-2xl border border-red-200 dark:border-red-900/30 shadow-sm text-center">
            <h3 className="text-xl font-medium text-red-600 dark:text-red-400 mb-2">No se pudo conectar con la API</h3>
            <p className="text-zinc-500 dark:text-zinc-400 mb-6">
              Asegúrate de que el servidor de Django esté corriendo en el puerto 8000.
            </p>
            <code className="bg-zinc-100 dark:bg-black px-4 py-3 rounded-lg text-sm text-left inline-block w-full max-w-md border border-zinc-200 dark:border-zinc-800">
              <span className="text-zinc-400"># En otra terminal, corre:</span><br/>
              python manage.py runserver
            </code>
          </div>
        ) : products.length === 0 ? (
          <div className="p-12 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 shadow-sm text-center">
            <p className="text-zinc-500 dark:text-zinc-400 text-lg">
              La conexión funciona, pero no hay productos en la base de datos.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((product: any) => (
              <div 
                key={product.id || product.slug} 
                className="group relative flex flex-col overflow-hidden rounded-2xl bg-white dark:bg-zinc-900/50 shadow-sm border border-zinc-200 dark:border-zinc-800/80 transition-all hover:shadow-lg hover:border-zinc-300 dark:hover:border-zinc-700 hover:-translate-y-1"
              >
                <div className="aspect-square bg-zinc-100 dark:bg-zinc-800/50 relative overflow-hidden">
                  {product.image || product.thumbnail ? (
                     <img 
                       src={product.image || product.thumbnail} 
                       alt={product.name || product.title} 
                       className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105" 
                     />
                  ) : (
                     <div className="flex items-center justify-center w-full h-full text-zinc-400 text-sm">
                       Sin Imagen
                     </div>
                  )}
                </div>
                <div className="p-5 flex-1 flex flex-col">
                  <h3 className="font-semibold text-lg line-clamp-2 text-zinc-900 dark:text-zinc-100">
                    {product.name || product.title}
                  </h3>
                  <div className="mt-auto pt-4 flex items-center justify-between">
                    <p className="text-blue-600 dark:text-blue-400 font-bold text-lg">
                      ${product.price}
                    </p>
                    <button className="h-8 w-8 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-600 dark:text-zinc-400 hover:bg-blue-600 hover:text-white transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
