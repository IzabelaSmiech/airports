# Importowanie niezbędnych bibliotek.
import pandas as pd
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt

# Importowanie pliku zawierającego dane o lotniskach używając pandas, wybranie potrzebnych kolumn.
airports = pd.read_csv('airport_volume_airport_locations.csv', \
    usecols=["Name","TotalSeats","Country Name","Airport1Latitude","Airport1Longitude"], \
         delimiter=',',encoding="utf8")

print(airports.sample(5))

# Wybranie porządanych krajów i zapisanie do nowej zmiennej - dane o lotniskach są dla całego świata. 
# Moim celem jest przedstawienie ich jedynie dla krajów Ameryki Południowej.
sa_airports = airports.loc[(airports['Country Name'] == 'Argentina') | (airports['Country Name'] == 'Brazil') \
    | (airports['Country Name'] == 'Chile') | (airports['Country Name'] == 'Colombia') \
        | (airports['Country Name'] == 'Venezuela') | (airports['Country Name'] == 'Paraguay') \
            | (airports['Country Name'] == 'Uruguay') | (airports['Country Name'] == 'Guyana') \
                | (airports['Country Name'] == 'Bolivia') | (airports['Country Name'] == 'Ecuador') \
                    | (airports['Country Name'] == 'Suriname') | (airports['Country Name'] == 'French Guiana') \
                        | (airports['Country Name'] == 'Peru')]
print(sa_airports)

# Stworzenie kolumny z geometrią.
sa_airports['geometry'] = sa_airports.apply(lambda row: Point(row['Airport1Longitude'], row['Airport1Latitude']), \
     axis=1)
print(sa_airports.sample(5))
print(type(sa_airports))

# DataFrame na GeoDataFrame używając geopandas.
geo_sa_airports = geopandas.GeoDataFrame(sa_airports, geometry='geometry')
geo_sa_airports.crs = {'init': 'epsg:4326'}

print(geo_sa_airports.sample(5))
print(type(geo_sa_airports))

# Sprawdzenie nazw kolumn używając pętli for
for val in sa_airports:
    print(val)

# Rzut okiem na dane:
geo_sa_airports.plot(figsize=(6,10), marker="o", markersize=20, alpha=0.4)
plt.show()

# Dane chciałam wyświelić na mapie - tworzenie mapy dla Ameryki Południowej:
# 1 - świat:
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# 2 - ograniczenie do Ameryki Południowej:
sa = world[world.continent == 'South America']
# Zamiana nazwy kolumn - potrzebna w późniejszym mergowaniu.
sa.columns=['pop_est','continent','Country Name','iso_a3','gdp_md_est','geometry']
print(sa.head())

# Stworzenie mapy, która wyświetla lotniska na obszarze Ameryki Południowej.
fig, ax = plt.subplots(1, figsize=(13,10))
sa_map = sa.plot(ax=ax, color='aliceblue', edgecolor='black')
geo_sa_airports.plot(ax=sa_map, figsize=(6,10), marker="o", markersize=20, alpha=0.6)
ax.set_title("Distribution of airports in South America")
plt.show()

# Tworzenie kartogramu - dzięki niemu można zoabczyć, które kraje mają najwięcej/najmniej lotnisk.

counts = geo_sa_airports.groupby('Country Name')['Name'].count().reset_index()
counts.columns = ['Country Name','num_airports']
counts = counts.sort_values(by='num_airports', ascending=False)
print(counts.head())

merging_data = counts.merge(sa)
merging_data = geopandas.GeoDataFrame(merging_data, geometry='geometry')
merging_data.crs = {'init': 'epsg:4326'}

merging_data.plot(column='num_airports', cmap='Blues', edgecolor='black', figsize=(13,10), legend=True)
plt.title('Distribution of airports in South America - choropleth')
plt.show()

# Flitrowanie danych pod kątem całkowitej liczba miejsc z ostatniego zgłoszonego roku.
# Jest to rok 2019. Wybrane dane to te, gdzie liczba miejsc przekroczyła 1 milion. 
# Ma to na celu wyłonienie największych lotnisk, które wykonały w 2019 najwięcej lotów. 
# Zapisane zostały za pomocą pętli do słownika, a następnie do DF, tak aby stworzyć wykres.
filtered = sa_airports.loc[sa_airports['TotalSeats'] > 1000000][['Name', 'TotalSeats']]
a_dict={}

# Tworzenie prostych pętli, oraz bardzo prostego wykresu słupkowego:
for name, seats in filtered.itertuples(index=False):
    a_dict[name] = seats

print(a_dict)
df = pd.DataFrame.from_dict(a_dict, orient='index')
print(df)

df.plot.bar(title='Total number of seats from year 2019 for airports with more that 1 milion seats.', \
     legend=False, position=0.5, rot=16)
plt.show()

b_dict={}
for name, seats in zip(sa_airports['Name'], sa_airports['TotalSeats']):
    b_dict[name] = seats

# Bardzo prosta funkcja sprawdzająca, czy szukane przez nas lotnisko jest w bazie danych:
def availability(airport):
    if airport in b_dict:
        print("Informations about airport", airport, "are available in this dataset")
    else:
        print("Informations about airport", airport, "are not available in this dataset")

availability('El Dorado Intl') 
availability('Antonio Jose de Sucre') 
availability('Modlin')